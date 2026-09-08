"""Run the frozen Classical BM25 formula with bounded-memory posting storage.

This is an evaluation execution adapter, not a complete Semantic OKF builder.
It uses the unchanged native normalizer, tokenizer, identities and BM25 scorer.
No questions, answers or relevance labels are accepted during index construction.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from contextlib import ExitStack
from dataclasses import asdict
import hashlib
import importlib.util
import json
import math
from pathlib import Path, PurePosixPath
import sqlite3
import stat
import struct
import sys
import time
import zipfile
import zlib

import numpy as np

BUCKETS = 64
HEADER = struct.Struct('<II')
POSTING = struct.Struct('<III')


def sha(path: Path) -> str:
    """Hash a regular file without reading it all into memory."""
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def write_json(path: Path, value: dict) -> None:
    """Create an append-only JSON artifact, rejecting non-finite values."""
    with path.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False)
        stream.write('\n')


def module(name: str, path: Path):
    """Import an explicitly supplied frozen implementation."""
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    sys.modules[name] = value
    spec.loader.exec_module(value)
    return value


def native(consultant: Path):
    """Load the standalone read-only Classical implementation."""
    return module('full_corpus_native_classical', consultant / 'scripts/_classical_snapshot.py')


def bucket(term: str) -> int:
    """Partition terms deterministically without changing their identities."""
    return zlib.crc32(term.encode('utf-8')) % BUCKETS


def connect(path: Path, readonly: bool = False):
    """Open an immutable published file or a private construction database."""
    if readonly:
        return sqlite3.connect(path.resolve().as_uri() + '?mode=ro&immutable=1', uri=True)
    connection = sqlite3.connect(path)
    connection.execute('PRAGMA journal_mode=OFF')
    connection.execute('PRAGMA synchronous=OFF')
    connection.execute('PRAGMA cache_size=-32768')
    return connection


def archive_records(archive_path: Path, manifest_path: Path, builder: Path):
    """Normalize every physical source document, preserving colliding IDs.

    A colliding upstream ID gets a path-bound internal suffix. Its original ID
    remains attached for evaluation and citations. No document is quarantined.
    """
    sys.path.insert(0, str(builder / 'scripts'))
    import _semantic_okf as core
    import _build_semantic_okf_core as adapter
    import re
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    sources = {row['id']: row for row in manifest['sources']}
    doc_id = re.compile(r'^(dsid_[0-9a-f]{32})__.+\.txt$')
    with zipfile.ZipFile(archive_path) as archive:
        members = []
        counts = Counter()
        for info in archive.infolist():
            path = PurePosixPath(info.filename)
            match = doc_id.fullmatch(path.name)
            if not match:
                continue
            if (path.is_absolute() or '..' in path.parts or '\\' in info.filename
                    or ':' in info.filename or stat.S_ISLNK(info.external_attr >> 16)):
                raise ValueError('Unsafe archive document member')
            source_id = path.parts[0].replace('_', '-')
            if source_id not in sources:
                raise ValueError('Undeclared source type')
            members.append((info, match[1], source_id))
            counts[match[1]] += 1
        for info, original_id, source_id in sorted(members, key=lambda row: row[0].filename):
            raw = archive.read(info)
            body = raw.decode('utf-8').replace('\r\n', '\n').replace('\r', '\n')
            if not body.strip():
                raise ValueError('Empty source document')
            identity = original_id
            if counts[identity] > 1:
                identity += '--' + hashlib.sha256(info.filename.encode()).hexdigest()[:16]
            title = body.splitlines()[0].strip() or original_id
            source = sources[source_id]
            input_path = manifest_path.parent / source['path']
            normalized = adapter._structured_record(source, input_path,
                                                     {'id': identity, 'title': title, 'body': body}, {})
            record = asdict(core.finalize_record(normalized, source,
                {'content_sha256': hashlib.sha256(raw).hexdigest()}, manifest, manifest_path.parent))
            if record['attributes']['body'] != body:
                raise ValueError('Native normalization lost original body')
            yield record, {'upstream_id': original_id, 'upstream_path': info.filename,
                           'raw_sha256': hashlib.sha256(raw).hexdigest(), 'raw_body': body,
                           'colliding_id': counts[original_id] > 1}


def ledger_records(path: Path):
    """Use an already validated ledger only for execution-adapter parity tests."""
    with path.open(encoding='utf-8') as stream:
        for line in stream:
            row = json.loads(line)
            body = row.get('attributes', {}).get('body', row['body'])
            yield row, {'upstream_id': row['record_id'], 'upstream_path': row['source_path'],
                        'raw_sha256': hashlib.sha256(body.encode()).hexdigest(),
                        'raw_body': body, 'colliding_id': False}


def build_index(rows, output: Path, plan: dict, implementation, batch_size: int = 4096) -> dict:
    """Create a complete query-independent inverted index in bounded blocks."""
    if output.exists():
        raise FileExistsError('Index destination already exists')
    implementation._validate_plan(plan)
    output.mkdir(parents=True)
    scratch = output / 'construction'
    scratch.mkdir()
    start = time.perf_counter()
    total = 0
    lengths = [0, 0]
    sources = Counter()
    original_chars = colliding_records = 0
    bound_records = hashlib.sha256()
    with ExitStack() as stack:
        streams = [stack.enter_context((scratch / f'{i:02d}.bin').open('xb')) for i in range(BUCKETS)]
        db = connect(output / 'documents.sqlite')
        stack.callback(db.close)
        db.execute('CREATE TABLE documents (number INTEGER PRIMARY KEY, document_id TEXT UNIQUE NOT NULL, '
                   'upstream_id TEXT NOT NULL, title_length INTEGER NOT NULL, body_length INTEGER NOT NULL, '
                   'payload BLOB NOT NULL)')
        db.execute('CREATE INDEX upstream_ids ON documents(upstream_id)')
        pending = {}

        def flush():
            for term, values in pending.items():
                encoded = term.encode('utf-8')
                stream = streams[bucket(term)]
                stream.write(HEADER.pack(len(encoded), len(values)))
                stream.write(encoded)
                stream.write(values)
            pending.clear()
            db.commit()

        for record, original in rows:
            derived = implementation._derive_documents([record], plan)
            if len(derived) != 1:
                raise ValueError('Enterprise full-record adapter requires exactly one passage')
            document = derived[0]
            for term in document['title_terms'].keys() | document['body_terms'].keys():
                if term not in pending:
                    pending[term] = bytearray()
                pending[term].extend(POSTING.pack(total, document['title_terms'].get(term, 0),
                                                document['body_terms'].get(term, 0)))
            lengths[0] += document['title_length']
            lengths[1] += document['body_length']
            payload = {key: value for key, value in document.items()
                       if key not in {'title_terms', 'body_terms', 'topic_weights'}}
            payload.update(original)
            encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, allow_nan=False).encode()
            db.execute('INSERT INTO documents VALUES (?,?,?,?,?,?)',
                       (total, document['document_id'], original['upstream_id'],
                        document['title_length'], document['body_length'], zlib.compress(encoded, 1)))
            bound_records.update((document['document_id'] + ':' + original['raw_sha256'] + '\n').encode())
            sources[document['source_id']] += 1
            original_chars += len(original['raw_body'])
            colliding_records += bool(original.get('colliding_id'))
            total += 1
            if total % batch_size == 0:
                flush()
                print(json.dumps({'phase': 'index', 'documents': total,
                                  'seconds': round(time.perf_counter()-start, 1)}), flush=True)
        flush()
    if not total:
        raise ValueError('Empty corpus')
    terms = postings = 0
    for partition in range(BUCKETS):
        combined = {}
        with (scratch / f'{partition:02d}.bin').open('rb') as stream:
            while header := stream.read(HEADER.size):
                term_size, data_size = HEADER.unpack(header)
                term = stream.read(term_size).decode('utf-8')
                data = stream.read(data_size)
                if len(data) != data_size or data_size % POSTING.size:
                    raise ValueError('Truncated posting block')
                combined.setdefault(term, bytearray()).extend(data)
        db = connect(output / f'terms-{partition:02d}.sqlite')
        try:
            db.execute('CREATE TABLE terms (term TEXT PRIMARY KEY, frequency INTEGER NOT NULL, '
                       'payload BLOB NOT NULL) WITHOUT ROWID')
            for term in sorted(combined):
                data = combined[term]
                frequency = len(data) // POSTING.size
                if not 0 < frequency <= total:
                    raise ValueError('Invalid document frequency')
                db.execute('INSERT INTO terms VALUES (?,?,?)', (term, frequency, zlib.compress(data, 1)))
                postings += frequency
            db.commit()
            terms += len(combined)
        finally:
            db.close()
        print(json.dumps({'phase': 'merge', 'buckets': partition+1, 'terms': terms}), flush=True)
    summary = {'schema_version': 'enterprise-classical-streaming/1.0', 'documents': total,
               'terms': terms, 'postings': postings, 'sources': dict(sources),
               'original_body_characters': original_chars, 'colliding_records_preserved': colliding_records,
               'average_field_lengths': {'title': round(lengths[0]/total, 10),
                                         'body': round(lengths[1]/total, 10)},
               'plan': plan, 'records_sha256': bound_records.hexdigest(),
               'native_implementation_sha256': sha(Path(implementation.__file__)),
               'construction_seconds': time.perf_counter()-start,
               'complete_semantic_okf_bundle': False,
               'files': {p.name: sha(p) for p in sorted(output.glob('*.sqlite'))}}
    write_json(output / 'index.json', summary)
    return summary


class Index:
    """Consult an immutable full-corpus index using the native BM25 formula."""

    def __init__(self, root: Path, implementation, verify: bool = True):
        self.root, self.native = root, implementation
        self.meta = json.loads((root / 'index.json').read_text(encoding='utf-8'))
        if sha(Path(implementation.__file__)) != self.meta['native_implementation_sha256']:
            raise ValueError('Frozen native implementation changed')
        if verify and any(sha(root / name) != digest for name, digest in self.meta['files'].items()):
            raise ValueError('Published index changed')
        self.db = connect(root / 'documents.sqlite', True)
        self.parts = [connect(root / f'terms-{i:02d}.sqlite', True) for i in range(BUCKETS)]
        rows = self.db.execute('SELECT number,document_id,title_length,body_length FROM documents ORDER BY number').fetchall()
        if len(rows) != self.meta['documents'] or [r[0] for r in rows] != list(range(len(rows))):
            raise ValueError('Index document inventory mismatch')
        self.ids = [r[1] for r in rows]
        self.title_lengths = np.array([r[2] for r in rows], dtype=np.float64)
        self.body_lengths = np.array([r[3] for r in rows], dtype=np.float64)

    def close(self):
        """Close every read-only handle."""
        self.db.close()
        for db in self.parts:
            db.close()

    def get(self, number: int) -> dict:
        """Hydrate exact stored evidence for one physical document."""
        row = self.db.execute('SELECT payload FROM documents WHERE number=?', (int(number),)).fetchone()
        if row is None:
            raise KeyError(number)
        result = json.loads(zlib.decompress(row[0]))
        if hashlib.sha256(result['text'].encode()).hexdigest() != result['text_sha256']:
            raise ValueError('Evidence text digest mismatch')
        return result

    def search(self, query: str, top_k: int = 10) -> list[dict]:
        """Score all matching documents with corpus-global native statistics.

        Vectorization identifies a conservative candidate set. The unchanged
        native scalar scorer recomputes its exact scores and tie ordering.
        """
        if not query.strip() or isinstance(top_k, bool) or not 1 <= top_k <= 1000:
            raise ValueError('Invalid query or cutoff')
        plan = self.meta['plan']
        weights = {k: float(v) for k, v in Counter(self.native.tokenize(query, plan)).items()}
        size = self.meta['documents']
        scores = np.zeros(size)
        terms, term_stats = {}, []
        config, average = plan['bm25'], self.meta['average_field_lengths']
        k1, b = float(config['k1']), float(config['b'])
        for term, weight in weights.items():
            row = self.parts[bucket(term)].execute('SELECT frequency,payload FROM terms WHERE term=?', (term,)).fetchone()
            if row is None:
                continue
            frequency, compressed = row
            values = np.frombuffer(zlib.decompress(compressed), dtype='<u4').reshape(-1, 3)
            numbers = values[:, 0]
            if len(values) != frequency or np.any(numbers[1:] <= numbers[:-1]):
                raise ValueError('Invalid posting identities')
            idf = round(math.log(1.0 + (size-frequency+0.5)/(frequency+0.5)), 10)
            field_scores = np.zeros(frequency)
            for column, field, lengths in ((1, 'title', self.title_lengths), (2, 'body', self.body_lengths)):
                tf = values[:, column].astype(np.float64)
                denominator = tf + k1*(1.0-b+b*lengths[numbers]/max(float(average[field]), 1e-12))
                field_scores += float(config[field+'_weight'])*tf*(k1+1.0)/denominator
            scores[numbers] += weight*idf*field_scores
            terms[term] = values
            term_stats.append({'term': term, 'idf': idf})
        positive = np.flatnonzero(scores > 0)
        if not len(positive):
            return []
        count = min(top_k, len(positive))
        boundary = np.partition(scores[positive], -count)[-count]
        tolerance = max(abs(boundary), 1.0)*1e-10
        candidates = positive[scores[positive] >= boundary-tolerance]
        documents = []
        by_identity = {}
        for number in candidates:
            row = self.get(int(number))
            by_identity[row['document_id']] = row
            row['title_terms'], row['body_terms'] = {}, {}
            for term, values in terms.items():
                position = int(np.searchsorted(values[:, 0], number))
                if position < len(values) and values[position, 0] == number:
                    row['title_terms'][term] = int(values[position, 1])
                    row['body_terms'][term] = int(values[position, 2])
            documents.append(row)
        exact = self.native._bm25_scores(documents, weights,
                   {'terms': term_stats, 'average_field_lengths': average}, plan)
        result = []
        for identity in self.native._rank(exact)[:top_k]:
            row = by_identity[identity]
            row.pop('title_terms'); row.pop('body_terms')
            result.append({**row, 'score': exact[identity], 'rank': len(result)+1})
        return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--consultant', type=Path, required=True)
    commands = parser.add_subparsers(dest='command', required=True)
    build = commands.add_parser('build')
    build.add_argument('--archive', type=Path)
    build.add_argument('--manifest', type=Path)
    build.add_argument('--builder', type=Path)
    build.add_argument('--records', type=Path)
    build.add_argument('--plan', type=Path, required=True)
    build.add_argument('--output', type=Path, required=True)
    query = commands.add_parser('search')
    query.add_argument('--index', type=Path, required=True)
    query.add_argument('--query', required=True)
    args = parser.parse_args()
    implementation = native(args.consultant)
    if args.command == 'build':
        if bool(args.records) == bool(args.archive):
            parser.error('Choose exactly one of --records or --archive')
        rows = ledger_records(args.records) if args.records else archive_records(args.archive, args.manifest, args.builder)
        result = build_index(rows, args.output, json.loads(args.plan.read_text()), implementation)
    else:
        index = Index(args.index, implementation)
        try:
            result = index.search(args.query)
        finally:
            index.close()
    print(json.dumps(result, ensure_ascii=False, allow_nan=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
