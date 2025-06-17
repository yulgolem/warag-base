# WBA Content Classification

The World Building Archivist (WBA) organizes information in the RAG store using **content types**. This **self‑organizing classification** system stores the types as meta‑documents. Each entry has the metadata field `{"category": "content-type"}` so they can be queried separately from ordinary text.

When a new piece of text is archived, the WBA attempts to match the provided type name against the stored meta‑documents:

1. The name is embedded and compared to the embeddings of all saved types.
2. If the best similarity exceeds the configured threshold, the existing type is reused.
3. Otherwise the name is tracked as a candidate. After it is seen a set number of times, a new type entry is automatically created.

This approach allows the archive to expand organically. Unknown labels evolve into formal types only when they appear frequently enough.

See the `ContentTypeManager` in `writeragents/agents/wba/classification.py` for the reference implementation.

## Faceted classification

Beyond simple content types the archivist can track arbitrary **facets** such as
`type` or `era`. Each facet is handled by a dedicated `ContentTypeManager`
instance within ``FacetManager``. When a facet value is seen often enough it is
saved as a meta-document with ``{"category": "facet-<name>"}``. Future archives
then store the normalized value in the chunk metadata.

## Configuration

The similarity threshold and candidate limit are defined in ``config/*.yaml``:

```yaml
wba:
  candidate_limit: 3
  classification_threshold: 0.8
```

Adjust these values to tune how aggressively new types are created.
