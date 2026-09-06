# Glyph-100M Parent-Document Split Audit

**Verdict: FAIL.**

- documents: `238,994`
- parent documents: `237,710`
- leaked parents: `5`
- chunks belonging to leaked parents: `486`
- missing split: `0`
- missing parent identity: `0`

## Leakage Examples

### wolne_lektury / argonauts-of-the-western-pacific

Splits: `train, val`; chunks: `149`

```json
[
  {
    "doc_id": "5edd9858b8bd67538918d1f3",
    "source_id": "argonauts-of-the-western-pacific#chunk-0000",
    "split": "train",
    "title": "Argonauts of the Western Pacific"
  },
  {
    "doc_id": "322a777edd1ee63a80f64641",
    "source_id": "argonauts-of-the-western-pacific#chunk-0001",
    "split": "train",
    "title": "Argonauts of the Western Pacific"
  },
  {
    "doc_id": "1f39b8caaad8b1cbe99f13dd",
    "source_id": "argonauts-of-the-western-pacific#chunk-0002",
    "split": "train",
    "title": "Argonauts of the Western Pacific"
  },
  {
    "doc_id": "2bf4f64031077e27a3439b88",
    "source_id": "argonauts-of-the-western-pacific#chunk-0003",
    "split": "train",
    "title": "Argonauts of the Western Pacific"
  }
]
```

### wolne_lektury / andrzejewski-miazga

Splits: `train, val`; chunks: `135`

```json
[
  {
    "doc_id": "6c1bbb12636b86adec0ce43e",
    "source_id": "andrzejewski-miazga#chunk-0000",
    "split": "train",
    "title": "Miazga"
  },
  {
    "doc_id": "92d74211d120500bc14ec30d",
    "source_id": "andrzejewski-miazga#chunk-0001",
    "split": "train",
    "title": "Miazga"
  },
  {
    "doc_id": "51824f87a195bb43191b9bd2",
    "source_id": "andrzejewski-miazga#chunk-0002",
    "split": "train",
    "title": "Miazga"
  },
  {
    "doc_id": "d97d5e730b5d25d59b130b6f",
    "source_id": "andrzejewski-miazga#chunk-0003",
    "split": "train",
    "title": "Miazga"
  }
]
```

### wolne_lektury / 20-000-mil-podmorskiej-zeglugi

Splits: `train, val`; chunks: `98`

```json
[
  {
    "doc_id": "c0d4dd2b0c0035ba7f963cb2",
    "source_id": "20-000-mil-podmorskiej-zeglugi#chunk-0000",
    "split": "val",
    "title": "20 000 mil podmorskiej żeglugi"
  },
  {
    "doc_id": "080ca78b3dacc0f6103f1ab8",
    "source_id": "20-000-mil-podmorskiej-zeglugi#chunk-0001",
    "split": "train",
    "title": "20 000 mil podmorskiej żeglugi"
  },
  {
    "doc_id": "5da48ebb93b9df50b1735801",
    "source_id": "20-000-mil-podmorskiej-zeglugi#chunk-0002",
    "split": "train",
    "title": "20 000 mil podmorskiej żeglugi"
  },
  {
    "doc_id": "143f7f95ccd067c9f88a548f",
    "source_id": "20-000-mil-podmorskiej-zeglugi#chunk-0003",
    "split": "val",
    "title": "20 000 mil podmorskiej żeglugi"
  }
]
```

### wolne_lektury / alejchem-z-jarmarku

Splits: `train, val`; chunks: `83`

```json
[
  {
    "doc_id": "4c0f45e8bd7d07381359ae4e",
    "source_id": "alejchem-z-jarmarku#chunk-0000",
    "split": "train",
    "title": "Z jarmarku"
  },
  {
    "doc_id": "6e0ef182c0053e56cacfdf3f",
    "source_id": "alejchem-z-jarmarku#chunk-0001",
    "split": "train",
    "title": "Z jarmarku"
  },
  {
    "doc_id": "89e73544ce248205e1569451",
    "source_id": "alejchem-z-jarmarku#chunk-0002",
    "split": "train",
    "title": "Z jarmarku"
  },
  {
    "doc_id": "83f89dcde87ae7ab77ce0d07",
    "source_id": "alejchem-z-jarmarku#chunk-0003",
    "split": "train",
    "title": "Z jarmarku"
  }
]
```

### wolne_lektury / aretino-zywoty-kurtyzan

Splits: `train, val`; chunks: `21`

```json
[
  {
    "doc_id": "18f9dd74ea444a02adbf4726",
    "source_id": "aretino-zywoty-kurtyzan#chunk-0000",
    "split": "train",
    "title": "Żywoty kurtyzan"
  },
  {
    "doc_id": "bc059a7bd1a74e942aea6244",
    "source_id": "aretino-zywoty-kurtyzan#chunk-0001",
    "split": "val",
    "title": "Żywoty kurtyzan"
  },
  {
    "doc_id": "05b8fa51a7e1c9381adff2c0",
    "source_id": "aretino-zywoty-kurtyzan#chunk-0002",
    "split": "train",
    "title": "Żywoty kurtyzan"
  },
  {
    "doc_id": "a9ed960b7adf92c2c50bacee",
    "source_id": "aretino-zywoty-kurtyzan#chunk-0003",
    "split": "train",
    "title": "Żywoty kurtyzan"
  }
]
```

