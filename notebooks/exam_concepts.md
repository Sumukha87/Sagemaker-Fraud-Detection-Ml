# MLA-C01 Exam Concepts — Quick Reference

Built up as each script is completed. Add new concepts after every script.

---

## Domain 1: Data Preparation (28%)

### S3 Data Formats
| Format | When to use | SageMaker built-in support |
|--------|------------|---------------------------|
| CSV | Simple, readable, slow for large data | Yes — most algorithms |
| Parquet | Columnar, fast reads, schema embedded | Yes — via Athena/Glue |
| RecordIO | Streaming, used by image/NLP algorithms | Yes — Pipe mode |
| ORC | Columnar like Parquet, Hive ecosystem | Via Glue |

Exam tip: SageMaker algorithms that support **Pipe mode** (streaming from S3) train faster and use less disk. File mode downloads the full dataset first.

### S3 URI Conventions in SageMaker
```
s3://bucket/prefix/train/data.csv      ← training channel
s3://bucket/prefix/validation/data.csv ← validation channel
s3://bucket/prefix/output/             ← model artifacts go here
```
SageMaker passes these as `InputDataConfig` channels to `create_training_job`.

---

*(More concepts added here as each script is built)*
