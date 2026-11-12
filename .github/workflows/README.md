# GitHub Actions

`offline.yml` runs the ordinary Python and frontend checks without cloud/provider
secrets or model downloads. The Python job installs an HTTP-denial pytest plugin.
Action revisions are pinned to verified upstream release commits.

`cloud-integration.yml` is manually dispatched, defaults off and requires protected
`main`, the repository variable `GLYCOLENS_CLOUD_TESTS_ENABLED=true`, and the
`glycolens-development` environment. Configure that environment's reviewers and
Supabase secrets before enabling it. No fork or pull-request event runs the job.
The job performs configuration preflight and the bounded P01 synthetic cloud
harness, with no model or paid-provider credentials. Hosted execution remains
pending while implementation stays local. The ordinary web job also installs the
pinned Playwright browser and runs isolated mocked journeys; its Supabase URL/key
are synthetic and cannot contact the real project.
