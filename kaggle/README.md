# Running the H2O wave hindcast example on Kaggle

Everything needed to publish and run
`us_doe_h2o_wave_hindcast_resource_characterization` as a public Kaggle notebook.

The notebook itself is unmodified in substance — it detects Kaggle at run time and
adapts. The same generated `.ipynb` still renders locally, and `make render-pdf`
still produces the same PDF.

## What this folder holds

| Path | Tracked | What it is |
|---|---|---|
| `build.sh` | yes | Stages `dataset/` and `notebook/` from the repo |
| `upload.sh` | yes | Pushes the staged dataset and notebook |
| `dataset-metadata.json` | yes | Kaggle dataset manifest — **edit the `id` before first upload** |
| `kernel-metadata.json` | yes | Notebook manifest: dataset attachment, internet toggle |
| `dataset/` | no | Exactly what gets uploaded: `cache/` + `h2o_examples/` |
| `notebook/` | no | Upload-ready `.ipynb`, outputs stripped, kernelspec normalized |

`dataset/` and `notebook/` are generated. Re-run `make kaggle-render` after warming
the cache or changing the `.qmd`.

## One-time setup

1. Install and authenticate the CLI: `pip install kaggle`, then put your API token
   at `~/.kaggle/kaggle.json` (Kaggle → Settings → API → Create New Token).
2. Edit `dataset-metadata.json` and replace `KAGGLE_USERNAME` in the `id` field
   with your Kaggle username.

## Publish

Two steps, kept separate so uploading an unchanged notebook does not cost a full
Quarto render:

```bash
make kaggle-render                        # render + stage (slow; only when .qmd changed)
make kaggle-upload                        # push dataset + notebook (fast)
make kaggle-upload M="add 2011 records"   # with a version message
```

`kaggle-upload` creates the dataset on the first run and versions it thereafter,
then pushes the notebook. The notebook arrives with the dataset already attached
and internet already enabled, from `kernel-metadata.json` — no checkboxes.

Both are private on first creation. Flip them to public together: a public
notebook backed by a private dataset fails for everyone else.

After the first upload, open the dataset and confirm `cache/` and `h2o_examples/`
appear as directories with their contents intact. A flattened upload is the most
common silent failure here — which is why `upload.sh` passes `--dir-mode zip`.

Then open the notebook and Run All, from a fresh session.

## How the notebook adapts

A bootstrap cell at the top of *Setup* does four things when it sees
`KAGGLE_KERNEL_RUN_TYPE`:

- installs `mhkit[wave]==1.1.*`, `itables` and `folium`;
- points `WORK_DIR` at `/kaggle/working`, so `figures/` and `.cache/` land in the
  writable output directory;
- adds the attached dataset to `sys.path` so `h2o_examples` imports;
- sets `H2O_RENDER_CONTEXT=dynamic` (via `setdefault`, so `make render-pdf` still
  wins locally), giving a live Folium map and interactive tables.

It then copies the dataset's `cache/` into `.cache/`. Copy, not read-through:
`load_site` and `contour` write their results back, and `/kaggle/input` is
read-only.

## Data: cache first, S3 second

The seeded cache is the **primary** path on Kaggle and live S3 is the fallback —
not the other way round. A cold contour recompute is hundreds of ~15 s fits and
will not finish inside a Kaggle session.

Nothing here needs credentials. `rex` opens the public `wpto-pds-us-wave` bucket
anonymously and unconditionally.

Override with `H2O_DATA_MODE`:

| Value | Behaviour |
|---|---|
| `auto` (default) | Use cached pickles when present, fetch from S3 otherwise |
| `cache` | Never touch S3; a missing key is a hard error |
| `live` | Ignore the seeded cache entirely, to prove the S3 path still works |

If a cache entry is missing *and* S3 is unreachable, the notebook raises early
with the list of missing files rather than quietly dropping sites from the
comparison.

## Internet

**Internet requires a phone-verified Kaggle account.** Without verification the API
accepts `enable_internet: true` and stores it, but the runtime never actually grants
networking — the symptom is `Temporary failure in name resolution` in the first cell,
which reads as a broken package rather than a permissions problem. Verify at
https://www.kaggle.com/settings.

The kernel needs internet **only for `pip install`**. The data cache itself works
offline. Running with the internet toggle fully off would mean pre-building
manylinux wheels for the whole `mhkit[wave]` tree — which have to be built on
Kaggle, not on macOS — and re-building them on every dependency bump. Not worth
it unless a competition rule forces it.

Note the Folium map still draws with the kernel offline: its tiles are fetched by
your browser, not the kernel.

## Gotchas

- `import rex` comes from **`nlr-rex`**, pulled in by `mhkit[wave]`. Never
  `pip install rex` — that is an unrelated project.
- Run All from a *fresh* session. The bootstrap cell can move `numpy`/`pandas`
  versions, and an already-imported module would go stale.
- Don't add a `"kaggle"` value to `H2O_RENDER_CONTEXT`. `map_render_context`
  raises `ValueError` on unknown presets. Kaggle selects the existing `dynamic`
  preset instead.
