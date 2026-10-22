# Oyun Odası 3B Modeli

**Site:** https://deniz.is-a.dev/oyun-odasi-3d/ (referansla karşılaştırma, tarayıcıda döndürülebilir model, render galerisi)

Bir zemin kat planının sol alt odası (plan dosyası gizlilik nedeniyle repoda yok), yapay zekâ ile üretilmiş referans görsel (`ref/render.jpg`) esas alınarak Blender 5.2'de tamamen Python ile prosedürel olarak modellendi.

## Çıktılar

| Dosya | İçerik |
|---|---|
| `out/oyun_odasi.blend` | Tam sahne (dokular gömülü, Geometry Nodes halı tüyü, ışıklar, 5 kamera) |
| `out/oyun_odasi.glb` | glTF, Draco sıkıştırmalı; sadeleştirilmiş malzemeler, halı tüyü ve bahçe yok |
| `out/final/01_ana_gorunum.png` | Referans açısından final render |
| `out/final/02…05_*.png` | Arka duvar, masa, kanepe ve aksonometrik kesit |
| `docs/` | GitHub Pages sitesi |

## Yeniden üretmek

```sh
python3 scene/gen_textures.py                         # ekran/poster dokuları (tex/ zaten hazır)
# sahneyi kur + render al (GPU/OptiX)
blender -b -P scene/build.py -- --out out/x.png --pct 100 --samples 256 [--cam main|back|desk|sofa|top] [--save out/x.blend]
python3 scene/post.py out/x.png out/x_post.png        # bloom + vinyet
scene/final_renders.sh                                # tüm final render'lar

# glTF dışa aktarma (kaydedilmiş .blend üzerinden)
blender -b out/oyun_odasi.blend -P scene/export_glb.py -- out/oyun_odasi.glb [--nodraco] [--lite]
```

Hızlı deneme için `--pct 50 --samples 64` (~10 sn), halı tüyünü kapatmak için `--nofur`.

## Modüller (`scene/`)

- `cfg.py` — ölçüler: oda 5,24 × 3,63 × 2,65 m, açıklıklar, masa, kamera
- `arch.py` — duvarlar, sürgülü cam, pencere + jaluzi, kapı, perdeler
- `joinery.py` — gömme raflar, konsol, ahşap/çıta duvarlar, pegboard, masa gövdesi
- `furniture.py` — yarış koltuğu, modüler kanepe, halılar (+ Geometry Nodes tüy), VR alanı, halka avize, ray spotlar
- `props.py` — monitörler, PC, klavye, gamepad, kulaklık, VR gözlükleri, figürler, kitaplar, saksılar
- `plants.py` — yaprak/ağaç üreteçleri
- `exterior.py` — teras, bahçe, uzak tepeler
- `materials.py` — beton, ahşap, kumaş, deri, halı, cam, gökyüzü kubbesi
- `lighting.py`, `post.py`, `camsolve.py` (referansa kamera eşleme), `backproj.py` (görselden plana geri izdüşüm)

## Bilinçli sapmalar

- AI görseldeki oda plandan ~%20 geniş; plan ölçüleri korundu, kamera 16 eşleme noktasıyla en küçük karelerle çözüldü.
- Batı penceresi planda 126 cm, görsele yaklaşmak için 151 cm.
- Ön plandaki alçak dolap referans kompozisyonu için odanın ortasında duruyor.
