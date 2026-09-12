# GitHub checkout layout

Clone the repositories into sibling directories:

```powershell
git clone https://github.com/bartaro/kitaqgb.git
git clone https://github.com/bartaro/kitaqfc.git
git clone https://github.com/bartaro/kokura.git
git clone https://github.com/bartaro/kurosaki.git
git clone https://github.com/bartaro/sarakura.git
git clone https://github.com/bartaro/kitaq-docs.git
```

Build the tools using each README, then run `./kitaq-docs/samples/build.ps1`
from their parent directory. The generated HTML is committed for offline use.
GitHub Pages can publish the `main` branch root with `.nojekyll`.

The verification screenshots and logs describe the recorded September 12
manual checks. The GitHub packaging build is documented separately in
`PUBLICATION_CHECKS.md`; it is not a claim of new physical-hardware testing.

GUI frontends and PLITA are deferred for this publication.
