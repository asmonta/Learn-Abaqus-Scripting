This repository provides four Python scripts of increasing complexity that demonstrate how to build, analyze, and postprocess finite element models in Abaqus using its scripting interface. Each script builds on the previous, illustrating key workflows and best practices in Abaqus automation.

All examples are based on a simple 3D cube with one face fixed and a point load applied to a corner node, providing a clear and minimal working example of structural simulation.

---

### `simple_cube_basic.py` – *Minimal Working Model*

This is the foundational script. It defines and runs a single Abaqus simulation of a solid cube:

- A cube (10×10×10) is created using an extruded square sketch.
- A linear elastic material is applied.
- One face is fully fixed (all DOFs constrained).
- A point load is applied to the top far corner of the cube.
- The part is meshed with a uniform seed size.
- A job is created and submitted via script.

> This script demonstrates the minimal set of commands needed to programmatically build and run a solid mechanics simulation in Abaqus.

---

### `simple_cube_refactored.py` – *Structured Class-Based Model*

This script takes the logic from `simple_cube_basic.py` and refactors it into a clean, object-oriented Python structure using classes and functions.

- The model logic is encapsulated in a `SimpleCubeModel` class.
- Each part of the simulation (geometry, materials, meshing, loads, boundary conditions, job submission) is defined in a dedicated method.
- The script follows a standard Python entry-point structure with a `main()` function.
- All inputs (geometry size, mesh density, material properties, load value) can be easily reused or overridden for larger workflows.

> This version is ideal for scaling to more complex models, teaching modular scripting practices, or embedding into larger pipelines like parametric sweeps or GUI-driven tools. That being said, just extensions are not require to produce Abaqus scripts, but is best practice. 

---


### `simple_cube_post.py` – *Adding Postprocessing*

This script extends the basic model by including **result extraction**:

- All functionality from the previous script is retained.
- After simulation completes, the output database is accessed using `openOdb`.
- The script extracts the **maximum von Mises stress** from the last frame of the simulation.
- A stress value is printed, and a CSV header is initialized for future data.

> This version introduces automated postprocessing and shows how to access and use result data within a script.

---

### `mesh_convergence.py` – *Mesh Convergence Study*

This is the most advanced script of the set, performing a **parametric study** varying the density of the mesh:

- The cube model is built and analyzed multiple times with varying mesh densities.
- For each mesh size, the simulation is run and postprocessed.
- The maximum von Mises stress is logged to a `.txt` file alongside its corresponding mesh size.
- Outputs are printed and appended line-by-line in CSV format, `stress_study.txt`.

> This script demonstrates how to automate design studies, such as mesh convergence checks or parameter sweeps, using structured scripting and file logging. This is generalizable to applying different loads or to modifying the geometry being analyzed

---

## Summary of Key Differences

| Feature                    |`simple_cube_basic.py`|`simple_cube_refactored.py`|`simple_cube_post.py`| `mesh_convergence.py` |
|-----------------|----|-----|-----|----|
| Model setup     | ✅ | ✅ | ✅ | ✅ |
| Refactored      | ❌ | ✅ | ✅ | ✅ |
| Postprocess ex. | ❌ | ❌ | ✅ | ✅ |
| Parametric ex.  | ❌ | ❌ | ❌ | ✅ |

---

