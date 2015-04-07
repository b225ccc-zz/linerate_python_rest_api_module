# LineRate Python REST API Module
A Python interface to the [LineRate](https://linerate.f5.com/) REST API

## Example

```python
import LinerateRestClient as lr_rest

# connect
client = lr_rest.Connection('172.16.87.153')

# get
print(client.get('/config/system/hostname'))

# set
client.put('/config/system/hostname', 'NEW_HOSTNAME')
```

## Convenience functions

### get_version()
```python
import LinerateRestClient as lr_rest

client = lr_rest.Connection('172.16.87.157')

client.get_version()
```

### write_mem()

```python
import LinerateRestClient as lr_rest

client = lr_rest.Connection('172.16.87.157')

client.write_mem()
```

## Notes

* Tested with Python 2.7
* LineRate [REST API docs](https://docs.lineratesystems.com/093Release_2.5/250REST_API_Reference_Guide)