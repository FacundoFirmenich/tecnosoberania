// LaNonApp desktop native wrapper — offline local server, zero external dependencies.
// Builds with Go standard library for Windows, Linux and macOS.
package main

import (
	"embed"
	"flag"
	"fmt"
	"io/fs"
	"log"
	"net"
	"net/http"
	"os"
	"os/exec"
	"runtime"
	"strings"
	"time"
)

//go:embed assets/app assets/site
var resources embed.FS

const version = "0.9.1-prealpha"

func openBrowser(addr string) error {
	var command *exec.Cmd
	switch runtime.GOOS {
	case "windows":
		command = exec.Command("rundll32", "url.dll,FileProtocolHandler", addr)
	case "darwin":
		command = exec.Command("open", addr)
	default:
		command = exec.Command("xdg-open", addr)
	}
	return command.Start()
}

func handler() http.Handler {
	content, err := fs.Sub(resources, "assets")
	if err != nil {
		panic(err)
	}
	static := http.FileServer(http.FS(content))
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.Method != "GET" && r.Method != "HEAD" {
			http.Error(w, "method not allowed", http.StatusMethodNotAllowed)
			return
		}
		host, _, err := net.SplitHostPort(r.Host)
		if err != nil || (host != "localhost" && host != "127.0.0.1" && host != "[::1]" && host != "::1") {
			http.Error(w, "host not allowed", http.StatusForbidden)
			return
		}
		w.Header().Set("X-Content-Type-Options", "nosniff")
		w.Header().Set("Referrer-Policy", "no-referrer")
		w.Header().Set("X-Frame-Options", "DENY")
		w.Header().Set("Cross-Origin-Resource-Policy", "same-origin")
		w.Header().Set("X-LaNonApp-Version", version)
		if strings.HasPrefix(r.URL.Path, "/api/") {
			http.NotFound(w, r)
			return
		}
		switch r.URL.Path {
		case "/", "/index.html":
			http.Redirect(w, r, "/app/index.html", http.StatusFound)
		case "/healthz":
			w.Header().Set("Content-Type", "text/plain; charset=utf-8")
			fmt.Fprint(w, "LaNonApp "+version+" OK")
		default:
			static.ServeHTTP(w, r)
		}
	})
}

func main() {
	port := flag.Int("port", 18765, "Local port (default 18765, stable browser storage origin; 0=random test only)")
	noBrowser := flag.Bool("no-browser", false, "Serve without opening the browser")
	versionFlag := flag.Bool("version", false, "Print version and exit")
	flag.Parse()
	if *versionFlag {
		fmt.Println("LaNonApp " + version)
		return
	}
	bind := fmt.Sprintf("127.0.0.1:%d", *port)
	ln, err := net.Listen("tcp", bind)
	if err != nil {
		// Another LaNonApp may already be serving this fixed origin. Never switch to a
		// random port silently, as the encrypted browser vault is bound to the origin.
		existingURL := fmt.Sprintf("http://127.0.0.1:%d/healthz", *port)
		client := &http.Client{Timeout: 2 * time.Second, Transport: &http.Transport{Proxy: nil}}
		if *port > 0 {
			if resp, requestErr := client.Get(existingURL); requestErr == nil {
				if resp.StatusCode == 200 && resp.Header.Get("X-LaNonApp-Version") == version {
					resp.Body.Close()
					fmt.Println("LaNonApp ya está abierta en este equipo; reutilizando la sesión")
					if !*noBrowser {
						if e := openBrowser(fmt.Sprintf("http://127.0.0.1:%d/app/index.html", *port)); e != nil {
							log.Print(e)
						}
					}
					return
				}
				resp.Body.Close()
			}
		}
		log.Fatalf("No se pudo reservar 127.0.0.1:%d: %v. LaNonApp no cambiará automáticamente de origen.", *port, err)
	}
	defer ln.Close()
	addr := "http://" + ln.Addr().String() + "/app/index.html"
	server := &http.Server{Handler: handler(), ReadHeaderTimeout: 5 * time.Second, IdleTimeout: 45 * time.Second}
	fmt.Println("LaNonApp " + version + " — solo en este equipo (127.0.0.1)")
	fmt.Println("Abrir: " + addr)
	fmt.Println("Cerrar la consola para detener el servidor. No es un sistema de emergencias.")
	if !*noBrowser {
		if err := openBrowser(addr); err != nil {
			fmt.Fprintln(os.Stderr, "Abrí el enlace manualmente:", err)
		}
	}
	if err := server.Serve(ln); err != nil && err != http.ErrServerClosed {
		log.Fatal(err)
	}
}
