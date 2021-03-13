## Arbitrium CLI

This command-line interface automate the generation of clients and the deployement of servers by creating and controlling a `docker container`

### FUD/Encoders

With few clicks the CLI will generate an undetectable ready-to-use client.

- Abstract synthax encoder: at each generation this encoder will create a client with a different size and a different source code but without impacting the functionnality of the client, which will make static analysis much harder for AVs, as soon an existing client become detectable, all you have to do is generate a new client which will hold a new source code. This encoder is still experimental and there is still a lot to do.

### Installation:
```bash
 $ pip2 install pyinquirer=1.0.3
 $ python2.7 main.py
```

### screenshots:

![pic1](https://user-images.githubusercontent.com/43894468/111032344-fda6b600-840b-11eb-8b33-c6770c9d6fed.png)

![pic2](https://user-images.githubusercontent.com/43894468/111032379-2929a080-840c-11eb-8d61-deef3c565644.png)

![pic3](https://user-images.githubusercontent.com/43894468/111032389-38105300-840c-11eb-91e5-b6c931b9fc9d.png)

![scan](https://user-images.githubusercontent.com/43894468/111032640-8e31c600-840d-11eb-8e03-b67dcd2fd196.png)


