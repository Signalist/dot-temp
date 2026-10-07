# Qualified W6 transfer input

The reduced 51-state Kundur model is inherited from the qualified ANDES 2.0.0 public benchmark, not a measured facility. The bundled model, adapter/export source, GPL notice and model-specific provenance are the only shared grid component copied into W6; no sibling branch is needed.

Expected reduced-model SHA256: `31e798abc23bdcb6c3b46aeb488caf96636127390935eac4d9f0e2fdd5601828` (15,314 bytes).

Original case: `kundur/kundur_full.xlsx`, SHA256 `f725e03ba12d8207616f68acdd606bbd35e7c4a68f13e66d7db43925adac2ed8`, supplied by official ANDES 2.0.0. Upstream source: https://github.com/CURENT/andes/tree/v2.0.0 . Keep `ANDES_LICENSE_GPL3.txt` and applicable upstream source/attribution obligations.

W6 matrix/kernel replay uses NumPy/SciPy and does not require ANDES. Fresh source regeneration requires a separately qualified ANDES environment and source-case hash verification. `grid_adapter.build('kundur')` followed by `grid_adapter.export_kundur_reduced(system, output_path)` specifies the reduction; it removes only the rotor-angle gauge. Do not call this nonlinear revalidation or a new hardware measurement.
