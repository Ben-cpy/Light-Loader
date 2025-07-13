package main

import (
	"fmt"
    "net/http"
    "os"
    "time"
)

func main() {
	start := time.Now()
    fmt.Println("Hello World")
	elapsed := time.Since(start)
	fmt.Printf("Hello World took %s\n", elapsed)

	start = time.Now()
    http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
        fmt.Fprintf(w, "Hello, %q", r.URL.Path)
    })
	elapsed = time.Since(start)
	fmt.Printf("http.HandleFunc took %s\n", elapsed)

	start = time.Now()
    fmt.Println(os.Getenv("HOME"))
	elapsed = time.Since(start)
	fmt.Printf("os.Getenv took %s\n", elapsed)

	start = time.Now()
    fmt.Println(time.Now())
	elapsed = time.Since(start)
	fmt.Printf("time.Now took %s\n", elapsed)
}