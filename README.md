# c-doxygen-parser
Generic Doxygen XML parser for C to easily allow for custom output.

Creates a list of python objects from Doxygen XML output for any C file containing:

* Structures
  * Structure Name
  * Structure Definitions
    * Structure Definition Type
    * Structure Definition Name
    * Structure Definition Description
* Enumerators
  * Enumerator Name
  * Enumerator Description
  * Enumerator Definitions
    * Enumerator Definition Name
* Functions
  * Function Name
  * Function Description
  * Function Paramaters
    * Function Paramater Name
    * Function Paramater Type
    * Function Paramater Description
    * Function Paramater Direction (In/Out)
* Macros
  * Macro Name
  * Macro Value
            
These can then be used to create a custom document.
