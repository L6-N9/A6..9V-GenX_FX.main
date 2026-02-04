# GenX Container Versions (GitHub + Cursor Secrets)

Your GitHub Packages container is:

- **Package**: `genx`
- **Registry image**: `ghcr.io/mouy-leng/genx`

## GitHub Actions (Repository Secrets)

Add these in **GitHub → Settings → Secrets and variables → Actions → Secrets**:

```
GENX_GHCR_IMAGE=ghcr.io/mouy-leng/genx
GENX_CONTAINER_DIGEST_MAIN=sha256:cbdd7132acf1cc3000d1965ac9ac0f7c8e425f0f2ac5e0080764e87279233f21
GENX_CONTAINER_DIGEST_2=sha256:3d8a19989bb281c070cc8b478317f904741a52e9ac18a4c3e9d15965715c9372
GENX_CONTAINER_DIGEST_3=sha256:c253aa7ab5d40949ff74f6aa00925087b212168efe8b7c4b60976c599ed11a76
```

## Cursor (Local Environment Variables)

Set the same names as **environment variables** in your local dev environment (or in Cursor’s environment settings), for example in your `.env` (gitignored):

```
GENX_GHCR_IMAGE=ghcr.io/mouy-leng/genx
GENX_CONTAINER_DIGEST_MAIN=sha256:cbdd7132acf1cc3000d1965ac9ac0f7c8e425f0f2ac5e0080764e87279233f21
GENX_CONTAINER_DIGEST_2=sha256:3d8a19989bb281c070cc8b478317f904741a52e9ac18a4c3e9d15965715c9372
GENX_CONTAINER_DIGEST_3=sha256:c253aa7ab5d40949ff74f6aa00925087b212168efe8b7c4b60976c599ed11a76
```

## Notes

- Digests are **immutable**: `image@sha256:...` always pulls the exact published image.
- These values are “version pins” (not passwords), but keeping them in Secrets avoids accidental logging and centralizes configuration.
