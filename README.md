# Jasper Client Python Library

## Installation

```sh
pip3 install jasperClient
```

## Utilisation

### Create a client instance

```python
from jasperClient.client import JasperClient

client = JasperClient("https://jasper.host/jasperserver/", "username", "password")
```

### Get a list of reports

```python
client.listReports()
```

### Get a dict with the required params of a report

```python
client.getParameters(path_of_the_report)
```

### Generate a report

```python
client.getReport(
    path=path_of_the_report,
    data=dict_with_report_params,
    filename="test",
    format="pdf",
)
```