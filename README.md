# SLE4442 Card Manager

This is a simple Python/Qt application meant to manage smartcards (memory cards) based on Siemens sle4442 chip.
With SLE4442 Card Manager you can perform all basic operations on you memory cards, 
including: inizialization, reading memory, presenting security PIN, changing PIN, writing to memory, permanently protecting the first 32 bytes from writing.

## Getting Started

SLE4442 memory cards are made of a main eeprom memory of 256 bytes, a PROM protection memory of 32 bits linked to first 32 bytes of main memory,
and a 4 bytes security memory.

Memory is freely readable once the card has been initialized and the connection established.
You must obviously have a smartcard reader capable of interfacing with this kind of cards.

In order to write to the card you must first enter the 3 bytes security PIN (usually set by manufacturers to 255,255,255).
Once acquired writing rights, you can write to main memory, the first 32 bytes of which can be permanently protected from further writing.
Once presented the right security PIN, you can also change it to a 3 bytes PIN of your choice.

All these operations can be performed using this little application.

### Prerequisites

In order to run SLE4442 Card Manager, you need Pyscard library.

you can find it here: https://github.com/LudovicRousseau/pyscard

### Installing

Just copy the files to your computer and run 'sle4442.py'

You can customize the gui editing the ui file.


## Authors

* **Francesco Fantoni** - [hvfrancesco](https://github.com/hvfrancesco)

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

Thanks to pyscard creators
