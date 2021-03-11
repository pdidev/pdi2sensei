## Changelog

# pdi2sensei 0.2.0

- No need for users to directly interact with data adaptor and analysis adaptor anymore, is replaced by the Bridge class
    - similar to the Endpoint jsut one class that is needed for usage
    - bridge class uses the needed adaptors for user
    - allows update intervals using timesteps and time intervalls


- Changed used mode of pycall in examples
    - use of the with statement allow much cleaner code in thy yaml files used to configure pdi2sensei


- Added to utility


- updated module file for jureca
- Bugfix: actually allow multiple Calayst scripts
