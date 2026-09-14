# Samples

Small local applications with explicit inputs and completion evidence. Run repository-level commands from the repository root. Python 3.12 or newer is the shared baseline; Docker and external scanner/policy binaries are separate optional prerequisites.

| Sample | Purpose | Starting point |
| --- | --- | --- |
| [Sample API](sample-api/README.md) | Shared read-only Flask reference with synthetic owners, explicit bearer tokens, API tests, container build and inventory | `make setup`, `make test`, then the sample's local startup command. |
| [Sample CLI](sample-cli/README.md) | Small local command-line exercise | Follow its documented inputs and error behavior. |

The API is the connected path through the [seven phases](../docs/roadmap.md), [labs](../labs/README.md), and [microservice capstone](../projects/microservice-api/README.md). It has no default authenticated user and no customer records. Its local server binds to loopback; the container example explicitly publishes a loopback-only host port.

Dependencies are declared and hash-locked. Keep tool configuration and test fixtures with the samples when copying them; the [template generator](../repo-templates/README.md) creates that complete reference directory. A normal test or build does not publish images, dispatch a release, provision cloud infrastructure, or install runtime sensors. Record optional environment results separately using the [validation matrix](../docs/validation.md).
