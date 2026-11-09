#requires -Version 5.1
<#
Publishes the site source to a separate, EXISTING GitHub repository.
It does NOT create a repository, enable GitHub Pages, modify DNS, or access credentials.
Usage: Right-click > Run with PowerShell, or from PowerShell: .\Publish_To_GitHub.ps1
#>
param(
    [string]$Repository = "Abdealmalk007/alghad-digital"
)
$ErrorActionPreference = "Stop"
$site = $PSScriptRoot
$repoUrl = "https://github.com/$Repository.git"
if ($Repository -notmatch '^[A-Za-z0-9-]+/[A-Za-z0-9._-]+$') {
    throw "Invalid GitHub repository name."
}
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    throw "Git is not installed or not on PATH."
}
foreach ($required in @("index.html", "CNAME", "assets/products.js", "assets/app.js", "assets/style.css")) {
    if (-not (Test-Path (Join-Path $site $required))) { throw "Missing: $required" }
}
Write-Host "[1/5] Checking public GitHub repository..." -ForegroundColor Cyan
$api = "https://api.github.com/repos/$Repository"
try {
    $response = Invoke-WebRequest -Uri $api -Headers @{"User-Agent"="Alghad-Site-Publisher"} -UseBasicParsing -TimeoutSec 20
    if ($response.StatusCode -ne 200) { throw "Unexpected HTTP status." }
} catch {
    throw "Repository is missing or not public. Create an EMPTY public repository at https://github.com/new named alghad-digital, then re-run. No files were changed."
}
Push-Location $site
try {
    Write-Host "[2/5] Running integrity checks..." -ForegroundColor Cyan
    if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
        throw "Python is required for SEO page generation and publication."
    }
    & python (Join-Path $site "scripts/prerender_home.py")
    if ($LASTEXITCODE -ne 0) { throw "Program-first static prerender failed" }
    & python (Join-Path $site "scripts/build_seo.py")
    if ($LASTEXITCODE -ne 0) { throw "SEO generation failed" }
    & python (Join-Path $site "scripts/build_support_pages.py")
    if ($LASTEXITCODE -ne 0) { throw "Support page generation failed" }
    & python (Join-Path $site "scripts/build_en.py")
    if ($LASTEXITCODE -ne 0) { throw "English language edition generation failed" }
    & python (Join-Path $site "scripts/test_seo.py")
    if ($LASTEXITCODE -ne 0) { throw "SEO integrity checks failed" }
    if (Get-Command node -ErrorAction SilentlyContinue) {
        & node (Join-Path $site "tests/bilingual-test.cjs")
        if ($LASTEXITCODE -ne 0) { throw "Arabic-English edition integrity tests failed" }
        & node (Join-Path $site "tests/favicon-test.cjs")
        if ($LASTEXITCODE -ne 0) { throw "Favicon asset integrity tests failed" }
        & node (Join-Path $site "tests/brand-seo-test.cjs")
    if ($LASTEXITCODE -ne 0) { throw "Brand SEO validation failed" }
    & node (Join-Path $site "tests/product-first-test.cjs")
        if ($LASTEXITCODE -ne 0) { throw "Product-first redesign integrity tests failed" }
        & node (Join-Path $site "tests/smoke-test.cjs")
        if ($LASTEXITCODE -ne 0) { throw "Site smoke tests failed" }
        & node (Join-Path $site "tests/two-actions-test.cjs")
        if ($LASTEXITCODE -ne 0) { throw "Download/share-only program actions validation failed" }
        & node (Join-Path $site "tests/editorial-test.cjs")
        if ($LASTEXITCODE -ne 0) { throw "Editorial data integrity tests failed" }
        & node (Join-Path $site "tests/industry-news-test.cjs")
        if ($LASTEXITCODE -ne 0) { throw "Official industry news validation failed" }
        & node (Join-Path $site "tests/translation-test.cjs")
        if ($LASTEXITCODE -ne 0) { throw "News translation validation failed" }
        if (Test-Path "C:\Program Files\Google\Chrome\Application\chrome.exe") {
            & node (Join-Path $site "tests/browser-test.cjs")
            if ($LASTEXITCODE -ne 0) { throw "Live Chrome integration tests failed" }
            & node (Join-Path $site "tests/nojs-browser-test.cjs")
            if ($LASTEXITCODE -ne 0) { throw "Chrome JavaScript-disabled fallback tests failed" }
        }
    } else {
        Write-Warning "Node is unavailable; static checks were skipped."
    }

    Write-Host "[3/5] Preparing Git repository..." -ForegroundColor Cyan
    if (-not (Test-Path (Join-Path $site ".git"))) { & git init -b main }
    if ($LASTEXITCODE -ne 0) { throw "git init failed" }
    $remoteNames = @(& git remote)
    $origin = if ($remoteNames -contains "origin") { & git remote get-url origin } else { $null }
    if ($origin) {
        if ($origin -notin @($repoUrl, "https://github.com/$Repository", "git@github.com:$Repository.git")) {
            throw "Existing origin points to a different repository. Aborting to prevent unintended changes."
        }
    } else {
        & git remote add origin $repoUrl
    }
    & git checkout -B main
    if ($LASTEXITCODE -ne 0) { throw "git checkout failed" }
    $safeFiles = @(
        ".gitignore", ".nojekyll", "CNAME", "index.html", "favicon.svg", "favicon.ico",
        "favicon-16.png", "favicon-32.png", "favicon-48.png",
        "apple-touch-icon.png", "icon-192.png", "icon-512.png", "site.webmanifest",
        "robots.txt", "sitemap.xml", "google3f39246447a165d6.html", "README.md", "DEPLOYMENT_AR.md",
        "Start_Preview.cmd", "Publish_To_GitHub.ps1",
        "assets/products.js", "assets/app.js", "assets/style.css", "assets/v2.css",
        "assets/v3.js", "assets/v3.css", "assets/v3_1.js", "assets/v3_1.css",
        "assets/downloads.js", "assets/downloads-ui.js", "assets/downloads.css",
        "assets/v3_3.js", "assets/v3_3.css", "assets/v3_4.js", "assets/v3_4.css", "assets/editorial.js", "assets/editorial.css", "assets/seo-pages.css", "assets/seo-home.css",
        "assets/news.json", "assets/news-data.js", "assets/tools.json", "assets/tools-data.js",
        "assets/industry-news.json", "assets/industry-news-data.js", "assets/industry-news.js", "assets/industry-news.css",
        "assets/translation-cache.json", "assets/product-first.css",
        "assets/language.css", "assets/en.css", "assets/en.js",
        "assets/release-facts.json", "assets/release-facts-data.js",
        "scripts/update_news.py", "scripts/update_industry_news.py", "scripts/translate_news.py",
        "scripts/prerender_home.py", "scripts/build_support_pages.py", "scripts/build_en.py", "scripts/update_release_facts.py", "scripts/generate_tool_art.py", "scripts/build_seo.py", "scripts/test_seo.py",
        "scripts/generate_social_preview.py", "scripts/generate_brand_icons.py", "assets/social/alghad-digital.png",
        ".github/workflows/update-tech-news.yml", ".well-known/security.txt",
        "tests/smoke-test.cjs", "tests/bilingual-test.cjs", "tests/brand-seo-test.cjs", "tests/product-first-test.cjs", "tests/nojs-browser-test.cjs", "tests/favicon-test.cjs", "tests/browser-test.cjs", "tests/editorial-test.cjs", "tests/industry-news-test.cjs", "tests/translation-test.cjs", "tests/share-download-test.cjs", "tests/no-duplicate-program-test.cjs", "tests/two-actions-test.cjs", "CHANGELOG.md"
    )
    $previewFiles = @(Get-ChildItem -LiteralPath (Join-Path $site "assets\previews") -File -Filter "*.svg" | ForEach-Object { "assets/previews/" + $_.Name })
    if ($previewFiles.Count -ne 10) { throw "Expected exactly 10 public program illustrations before publication." }
    $safeFiles += $previewFiles
    $toolImages = @(Get-ChildItem -LiteralPath (Join-Path $site "assets\tools") -File -Filter "*.svg" | ForEach-Object { "assets/tools/" + $_.Name })
    if ($toolImages.Count -ne 8) { throw "Expected exactly 8 original Windows utilities illustrations." }
    $safeFiles += $toolImages
    $seoPages = @(
        Get-ChildItem -LiteralPath (Join-Path $site "programs") -Recurse -File -Filter "index.html" |
        ForEach-Object { $_.FullName.Substring($site.Length + 1).Replace("\", "/") }
    )
    $seoPages += @("news/index.html", "free-windows-tools/index.html", "ai-news/index.html", "tech-companies/index.html", "cars/index.html", "protech/index.html", "about/index.html", "security/index.html", "privacy/index.html")
    if ($seoPages.Count -ne 20) {
        throw "Expected 20 searchable program, developer, news and support pages."
    }
    $safeFiles += $seoPages
    $englishPages = @(
        Get-ChildItem -LiteralPath (Join-Path $site "en") -Recurse -File -Filter "index.html" |
        ForEach-Object { $_.FullName.Substring($site.Length + 1).Replace("\", "/") }
    )
    if ($englishPages.Count -ne 21) {
        throw "Expected exactly 21 static English pages matching the 21 Arabic canonical pages."
    }
    $safeFiles += $englishPages
    & git add -- $safeFiles
    if ($LASTEXITCODE -ne 0) { throw "Git add failed" }
    # Track deletion of previously published preview files as well.
    & git add -u -- assets/previews
    if ($LASTEXITCODE -ne 0) { throw "Failed to stage preview deletions" }
    if ($LASTEXITCODE -ne 0) { throw "git add failed" }
    $staged = (& git diff --cached --name-only)
    if ($staged) {
        Write-Host "[4/5] Committing approved public files..." -ForegroundColor Cyan
        & git commit -m "Publish Alghad Digital software showcase"
        if ($LASTEXITCODE -ne 0) { throw "Commit failed. Configure Git name/email safely, then retry." }
    } else {
        Write-Host "[4/5] No changes to commit."
    }
    Write-Host "[5/5] Pushing to GitHub using Git Credential Manager..." -ForegroundColor Cyan
    & git push -u origin main
    if ($LASTEXITCODE -ne 0) { throw "Push failed. Review GitHub authentication/permissions." }
    Write-Host "Source published: https://github.com/$Repository" -ForegroundColor Green
    Write-Host "NEXT: Settings > Pages > Deploy from a branch > main / (root)." -ForegroundColor Yellow
    Write-Host "Configure custom domain alghad.digital in Pages BEFORE changing DNS." -ForegroundColor Yellow
} finally {
    Pop-Location
}