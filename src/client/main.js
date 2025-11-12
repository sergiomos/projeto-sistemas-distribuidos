#!/usr/bin/env node
const zmq = require('zeromq');
const msgpack = require('msgpack-lite');
const readline = require('readline');

class Client {
    constructor() {
        this.reqSocket = null;
        this.subSocket = null;
        this.username = null;
        this.logicalClock = 0;
    }

    updateClock(receivedClock = 0) {
        this.logicalClock = Math.max(this.logicalClock, receivedClock) + 1;
    }

    incrementClock() {
        this.logicalClock++;
    }

    async connect() {
        // Socket REQ para requisições ao broker
        this.reqSocket = new zmq.Request();
        await this.reqSocket.connect("tcp://broker:5555");
        
        // Socket SUB para receber publicações do proxy (será usado na Parte 2)
        this.subSocket = new zmq.Subscriber();
        await this.subSocket.connect("tcp://proxy:5558");
        
        console.log("Cliente conectado ao broker e proxy");
    }

    async sendRequest(service, data) {
        this.incrementClock();
        
        const message = {
            service: service,
            data: {
                ...data,
                timestamp: new Date().toISOString(),
                clock: this.logicalClock
            }
        };
        
        const packed = msgpack.encode(message);
        await this.reqSocket.send(packed);
        const [response] = await this.reqSocket.receive();
        const decoded = msgpack.decode(response);
        
        this.updateClock(decoded.data?.clock || 0);
        return decoded;
    }

    async login(username) {
        const response = await this.sendRequest("login", { user: username });
        
        if (response.data.status === "sucesso") {
            this.username = username;
            console.log(`Login bem-sucedido: ${username}`);
            
            // Inscreve no próprio nome para receber mensagens (Parte 2)
            this.subSocket.subscribe(username);
            return true;
        } else {
            console.log(`Erro no login: ${response.data.description}`);
            return false;
        }
    }

    async listUsers() {
        const response = await this.sendRequest("users", {});
        console.log("Usuários cadastrados:", response.data.users);
        return response.data.users;
    }

    async createChannel(channelName) {
        const response = await this.sendRequest("channel", { channel: channelName });
        
        if (response.data.status === "sucesso") {
            console.log(`Canal criado: ${channelName}`);
        } else {
            console.log(`Erro ao criar canal: ${response.data.description}`);
        }
    }

    async listChannels() {
        const response = await this.sendRequest("channels", {});
        console.log("Canais disponíveis:", response.data.channels);
        return response.data.channels;
    }

    async publishToChannel(channel, message) {
        const response = await this.sendRequest("publish", {
            user: this.username,
            channel: channel,
            message: message
        });
        
        if (response.data.status === "OK") {
            console.log(`Mensagem publicada no canal ${channel}`);
        } else {
            console.log(`Erro: ${response.data.message}`);
        }
    }

    async sendMessage(toUser, message) {
        const response = await this.sendRequest("message", {
            src: this.username,
            dst: toUser,
            message: message
        });
        
        if (response.data.status === "OK") {
            console.log(`Mensagem enviada para ${toUser}`);
        } else {
            console.log(`Erro: ${response.data.message}`);
        }
    }

    async subscribeToChannel(channel) {
        this.subSocket.subscribe(channel);
        console.log(`Inscrito no canal: ${channel}`);
    }

    startListening() {
        (async () => {
            for await (const [topic, msg] of this.subSocket) {
                const topicStr = topic.toString();
                const data = msgpack.decode(msg);
                
                this.updateClock(data.clock || 0);
                
                if (topicStr === this.username) {
                    // Mensagem privada
                    console.log(`\n[Clock=${this.logicalClock}] [MSG de ${data.src}]: ${data.message}`);
                } else {
                    // Publicação em canal
                    console.log(`\n[Clock=${this.logicalClock}] [${topicStr}] ${data.user}: ${data.message}`);
                }
            }
        })();
    }

    showMenu() {
        console.log("\n=== Menu ===");
        console.log("1. Listar usuários");
        console.log("2. Criar canal");
        console.log("3. Listar canais");
        console.log("4. Inscrever em canal");
        console.log("5. Publicar em canal");
        console.log("6. Enviar mensagem privada");
        console.log("7. Sair");
        console.log("============\n");
    }

    async run() {
        await this.connect();
        
        const rl = readline.createInterface({
            input: process.stdin,
            output: process.stdout
        });

        // Função para fazer perguntas
        const question = (prompt) => {
            return new Promise((resolve) => {
                rl.question(prompt, resolve);
            });
        };

        // Login
        while (!this.username) {
            const username = await question("Digite seu nome de usuário: ");
            await this.login(username.trim());
        }

        // Inicia listener de mensagens
        this.startListening();

        // Menu principal
        let running = true;
        while (running) {
            this.showMenu();
            const choice = await question("Escolha uma opção: ");

            switch (choice.trim()) {
                case '1':
                    await this.listUsers();
                    break;
                case '2':
                    const channelName = await question("Nome do canal: ");
                    await this.createChannel(channelName.trim());
                    break;
                case '3':
                    await this.listChannels();
                    break;
                case '4':
                    const subChannel = await question("Canal para se inscrever: ");
                    await this.subscribeToChannel(subChannel.trim());
                    break;
                case '5':
                    const pubChannel = await question("Canal: ");
                    const pubMessage = await question("Mensagem: ");
                    await this.publishToChannel(pubChannel.trim(), pubMessage);
                    break;
                case '6':
                    const toUser = await question("Para usuário: ");
                    const privateMsg = await question("Mensagem: ");
                    await this.sendMessage(toUser.trim(), privateMsg);
                    break;
                case '7':
                    console.log("Encerrando...");
                    running = false;
                    break;
                default:
                    console.log("Opção inválida!");
            }
        }

        rl.close();
        this.reqSocket.close();
        this.subSocket.close();
    }
}

// Inicia o cliente
const client = new Client();
client.run().catch(console.error);
