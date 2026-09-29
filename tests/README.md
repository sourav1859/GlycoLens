# Cross-System Tests

Integration and end-to-end tests spanning the frontend, backend, database, and external-service adapters will be organized here.

The implemented research-data tests use synthetic CSV fixtures and contain no downloaded or row-level health data. Run them with:

```powershell
python -m unittest tests.research.test_t1d_uom -v
```
