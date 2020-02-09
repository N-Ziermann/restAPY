# restAPY
**Version 1.0.1**

A python module for building Rest APIs



## Example

```python
import restAPY
api = restAPY.API(80, “0.0.0.0”)
api.setPath(“/”, {“celsius”:5, “fahrenheit”:41})
api.run()
```

Done! Start the python file and you've got a working rest API.



## Installation

Inside the terminal:

```bash
pip install restAPY
```

Inside your project:

```python
import restAPY
```



## Dependencies

#### Python 3.6 (or higher) with the following modules:

- socket
- threading
- json
- ssl

All of these are part of the default python install and therefore don't need to be installed separately.



## Documentation

https://restapy.readthedocs.io/




## Contributors

Niklas Ziermann



## Copyright & License

**© Niklas Ziermann** 

**MIT License**

