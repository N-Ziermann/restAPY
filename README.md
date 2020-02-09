# restAPY [![Tweet](https://img.shields.io/twitter/url/http/shields.io.svg?style=social)](https://twitter.com/intent/tweet?text=Just%20found%20this%20python%20module%20for%20creating%20rest%20APIs%20from%20@NiklasZiermann.%20I%20think%20you%20should%20take%20a%20look&hashtags=API,restAPI,python,web,developers) [![Open Source Love](https://badges.frapsoft.com/os/mit/mit.svg?v=102)](https://github.com/N-Ziermann/restAPY/blob/master/LICENSE) [![pypi](http://githubbadges.com/star.svg?user=n-ziermann&repo=restAPY&style=flat)](https://github.com/N-Ziermann/restAPY) [![star this repo](https://img.shields.io/pypi/v/restAPY)](https://pypi.org/project/restAPY/)

![alt text](https://github.com/N-Ziermann/restAPY/blob/master/logo.png "Logo Title Text 2")

## Version 1.0.1

## A python module for building Rest APIs

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

