The real logo files. Never redraw, recolour or stretch them.

## FLIK

- `flik-wordmark.svg`: the full FLIK wordmark (90 × 32). The F is `flik-orange` (#F26324), the LIK letters are `flik-navy` (#232356 and #222255). Use in headers at 30px tall, on `surface` or `surface-alt`.
- `flik-mark.svg`: the orange F mark alone (30 × 30), in `flik-orange`. Use as the app icon, the dashboard account switcher (16–28px), favicons, and on a white tile over the `dark` band.

Both are full-colour SVGs (not single-ink), so they do not change colour with CSS.

## Partners (`payment/`, `courier/`, `platform/`)

Square 24px icons of the banks, e-wallets, QRIS, couriers and sales and ad platforms FLIK works with, as SVG and as a 96px PNG (4×). They keep their own colours. Show them with the `PartnerLogo` component (`fl-plogo`), always next to the name.

- **Use the PNG.** The courier and platform SVGs only wrap a bitmap and weigh up to 466 KB; the PNGs are 2–6 KB and stay sharp up to 48px. The payment SVGs are true vectors except `ovo.svg`.
- **Payment (11):** bca, bni, bri, bsi, mandiri, permata, dana, gopay, ovo, qris, shopeepay.
- **Courier (18):** anteraja, deliveree, gosend, grabexpress, idexpress, jne, jnt, lalamove, lionparcel, mrspeedy, ninjaxpress, paxel, rpx, sap, sicepat, spx, tiki, wahana. `spx.png` (160px, PNG only) comes from the dashboard's earlier courier set.
- **Platform (12):** blibli, googleads, lazada, magento1, magento2, metaads, shopee, shopify, tiktok, tokopedia, woocommerce, zalora. Use `tiktok`, `shopee` and `tokopedia` for their ads products too (TikTok Ads, Shopee Ads, Tokopedia Ads).
- Not in the set yet: Visa, Mastercard and other card networks, and COD (FLIK's own method). Show those, and channels with no brand (offline store, other), with the `fl-plogo--icon` tile and a line icon.
- File names are lowercase brand keys; add new partners the same way (both formats, 24px viewBox, 96px PNG).
