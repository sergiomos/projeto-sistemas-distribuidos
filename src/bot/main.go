package main

import (
	"fmt"
	"math/rand"
	"time"

	"github.com/vmihailenco/msgpack/v5"
	zmq "github.com/pebbe/zmq4"
)

type Message struct {
	Service string                 `msgpack:"service"`
	Data    map[string]interface{} `msgpack:"data"`
}

type Bot struct {
	reqSocket    *zmq.Socket
	subSocket    *zmq.Socket
	username     string
	logicalClock int
}

func (b *Bot) updateClock(receivedClock int) {
	if receivedClock > b.logicalClock {
		b.logicalClock = receivedClock
	}
	b.logicalClock++
}

func (b *Bot) incrementClock() {
	b.logicalClock++
}

func NewBot() (*Bot, error) {
	reqSocket, err := zmq.NewSocket(zmq.REQ)
	if err != nil {
		return nil, err
	}

	subSocket, err := zmq.NewSocket(zmq.SUB)
	if err != nil {
		return nil, err
	}

	return &Bot{
		reqSocket: reqSocket,
		subSocket: subSocket,
	}, nil
}

func (b *Bot) Connect() error {
	if err := b.reqSocket.Connect("tcp://broker:5555"); err != nil {
		return err
	}

	if err := b.subSocket.Connect("tcp://proxy:5558"); err != nil {
		return err
	}

	fmt.Println("Bot conectado ao broker e proxy")
	return nil
}

func (b *Bot) SendRequest(service string, data map[string]interface{}) (map[string]interface{}, error) {
	b.incrementClock()
	
	data["timestamp"] = time.Now().Format(time.RFC3339)
	data["clock"] = b.logicalClock

	msg := Message{
		Service: service,
		Data:    data,
	}

	msgBytes, err := msgpack.Marshal(msg)
	if err != nil {
		return nil, err
	}

	if _, err := b.reqSocket.SendBytes(msgBytes, 0); err != nil {
		return nil, err
	}

	respBytes, err := b.reqSocket.RecvBytes(0)
	if err != nil {
		return nil, err
	}

	var response map[string]interface{}
	if err := msgpack.Unmarshal(respBytes, &response); err != nil {
		return nil, err
	}

	// Atualiza relógio com resposta
	if data, ok := response["data"].(map[string]interface{}); ok {
		if clock, ok := data["clock"].(int); ok {
			b.updateClock(clock)
		}
	}

	return response, nil
}

func (b *Bot) Login() error {
	// Gera nome de usuário aleatório
	rand.Seed(time.Now().UnixNano())
	b.username = fmt.Sprintf("bot_%d", rand.Intn(100000))

	response, err := b.SendRequest("login", map[string]interface{}{
		"user": b.username,
	})
	if err != nil {
		return err
	}

	data := response["data"].(map[string]interface{})
	if data["status"] == "sucesso" {
		fmt.Printf("Bot logado: %s\n", b.username)
		// Inscreve no próprio nome
		b.subSocket.SetSubscribe(b.username)
		return nil
	}

	return fmt.Errorf("erro no login: %v", data["description"])
}

func (b *Bot) GetChannels() ([]string, error) {
	response, err := b.SendRequest("channels", map[string]interface{}{})
	if err != nil {
		return nil, err
	}

	data := response["data"].(map[string]interface{})
	channelsRaw := data["channels"].([]interface{})

	channels := make([]string, len(channelsRaw))
	for i, ch := range channelsRaw {
		channels[i] = ch.(string)
	}

	return channels, nil
}

func (b *Bot) PublishToChannel(channel, message string) error {
	response, err := b.SendRequest("publish", map[string]interface{}{
		"user":    b.username,
		"channel": channel,
		"message": message,
	})
	if err != nil {
		return err
	}

	data := response["data"].(map[string]interface{})
	if data["status"] == "OK" {
		fmt.Printf("[Clock=%d] [%s] Publicou: %s\n", b.logicalClock, channel, message)
		return nil
	}

	return fmt.Errorf("erro ao publicar: %v", data["message"])
}

func (b *Bot) Run() {
	messages := []string{
		"Olá, sou um bot!",
		"Mensagem automática",
		"Testando o sistema",
		"Bot em ação",
		"Mensagem de teste",
		"Sistema funcionando",
		"Publicação automática",
		"Bot ativo",
		"Teste de carga",
		"Mensagem gerada automaticamente",
	}

	for {
		// Busca canais disponíveis
		channels, err := b.GetChannels()
		if err != nil {
			fmt.Printf("Erro ao buscar canais: %v\n", err)
			time.Sleep(5 * time.Second)
			continue
		}

		if len(channels) == 0 {
			fmt.Println("Nenhum canal disponível. Aguardando...")
			time.Sleep(5 * time.Second)
			continue
		}

		// Escolhe canal aleatório
		channel := channels[rand.Intn(len(channels))]

		// Envia 10 mensagens
		for i := 0; i < 10; i++ {
			message := messages[rand.Intn(len(messages))]
			if err := b.PublishToChannel(channel, message); err != nil {
				fmt.Printf("Erro: %v\n", err)
			}
			time.Sleep(1 * time.Second)
		}

		// Pausa entre ciclos
		time.Sleep(2 * time.Second)
	}
}

func (b *Bot) Close() {
	b.reqSocket.Close()
	b.subSocket.Close()
}

func main() {
	bot, err := NewBot()
	if err != nil {
		fmt.Printf("Erro ao criar bot: %v\n", err)
		return
	}
	defer bot.Close()

	if err := bot.Connect(); err != nil {
		fmt.Printf("Erro ao conectar: %v\n", err)
		return
	}

	if err := bot.Login(); err != nil {
		fmt.Printf("Erro no login: %v\n", err)
		return
	}

	bot.Run()
}

