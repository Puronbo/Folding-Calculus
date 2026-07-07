## Mirror Setup Checklist

### GitLab
1. Create account at https://gitlab.com
2. Create repo: `Puronbo/Folding-Calculus` (public)
3. Go to https://gitlab.com/-/user_settings/personal_access_tokens
4. Create a token with `write_repository` scope
5. Add to GitHub repo secrets as `GITLAB_TOKEN`

### Codeberg
1. Create account at https://codeberg.org
2. Create repo: `Puronbo/Folding-Calculus` (public)
3. Go to https://codeberg.org/user/settings/applications
4. Create a token with `write_repository` scope
5. Add to GitHub repo secrets as `CODEBERG_TOKEN`
6. Add your Codeberg username as `CODEBERG_USERNAME`

### Internet Archive
1. Create account at https://archive.org
2. Go to https://archive.org/account/s3.php
3. Generate S3 keys
4. Run: `ia configure` locally
5. Upload: `ia upload puno-calculus-v1 C:\path\to\tarball.tar.gz --metadata="title:The Puno Calculus" --metadata="creator:Michael Grafiel Sayson Puno"`

### Zenodo DOI
1. Go to https://zenodo.org
2. Link GitHub account
3. Enable repo: `Puronbo/Folding-Calculus`
4. Create a new release → Zenodo auto-assigns DOI
5. Update `DISTRIBUTION.md` and README badge with DOI
