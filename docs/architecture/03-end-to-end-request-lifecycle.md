# End-to-End Request Lifecycle

## Developer Request
A developer runs:

```bash
idpctl create-service payments-api \
  --template fastapi \
  --team checkout \
  --env dev