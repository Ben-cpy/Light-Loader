package function

var LargeData string

func init() {
	data := make([]byte, 10000000)
	for i := 0; i < 10000000; i++ {
		data[i] = 'a'
	}
	LargeData = string(data)
}

// need format
