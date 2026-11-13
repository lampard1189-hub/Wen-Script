# Wen Script — Public Alpha 0.1

Wen Script is an experimental, reversible writing system. This repository contains a small static website that converts English text into Wen symbols and decodes the symbols back into English.

## Try it locally
Open `index.html` in a modern browser. No build step or server is required.

## Publish it with GitHub Pages
1. Create a public repository named `wen-script`.
2. Upload `index.html` and the `assets/` folder to the repository root.
3. In the repository, open **Settings → Pages**.
4. Under Build and deployment, choose **Deploy from a branch**.
5. Select the `main` branch and `/ (root)`, then save.
6. GitHub will provide the public website address when deployment finishes.

## Encoding notes
- The alphabet maps A–Z to 26 fixed symbols.
- Digits and common punctuation have separate mappings.
- Spaces are represented by a full-width space.
- The optional binary guide adds a five-bit alphabet index after each letter.
- This is a substitution alphabet, **not encryption**. It should not be used to protect secrets.
- Version 0.1 supports basic English text. Accents and many Unicode characters are preserved unchanged.

## Project status
Public alpha. The alphabet and punctuation mapping may evolve before a stable 1.0 release. A future release should define a formal Unicode normalization policy, casing rules, and a versioned specification.

## License
MIT License. See `LICENSE`.
