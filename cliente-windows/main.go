package main

import (
	"fmt"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"runtime"
	"sync/atomic"
	"syscall"
	"time"
	"unsafe"
)

var (
	user32               = syscall.NewLazyDLL("user32.dll")
	kernel32             = syscall.NewLazyDLL("kernel32.dll")
	gdi32                = syscall.NewLazyDLL("gdi32.dll")
	procMessageBoxW      = user32.NewProc("MessageBoxW")
	procRegisterClassExW = user32.NewProc("RegisterClassExW")
	procCreateWindowExW  = user32.NewProc("CreateWindowExW")
	procDefWindowProcW   = user32.NewProc("DefWindowProcW")
	procShowWindow       = user32.NewProc("ShowWindow")
	procUpdateWindow     = user32.NewProc("UpdateWindow")
	procGetMessageW      = user32.NewProc("GetMessageW")
	procTranslateMessage = user32.NewProc("TranslateMessage")
	procDispatchMessageW = user32.NewProc("DispatchMessageW")
	procPostQuitMessage  = user32.NewProc("PostQuitMessage")
	procPostMessageW     = user32.NewProc("PostMessageW")
	procDestroyWindow    = user32.NewProc("DestroyWindow")
	procSetWindowTextW   = user32.NewProc("SetWindowTextW")
	procGetSystemMetrics = user32.NewProc("GetSystemMetrics")
	procCreateFontW      = gdi32.NewProc("CreateFontW")
	procSendMessageW     = user32.NewProc("SendMessageW")
	procGetModuleHandleW = kernel32.NewProc("GetModuleHandleW")
)

const (
	WS_OVERLAPPED       = 0x00000000
	WS_CAPTION          = 0x00C00000
	WS_SYSMENU          = 0x00080000
	WS_MINIMIZEBOX      = 0x00020000
	WS_VISIBLE          = 0x10000000
	WS_CHILD            = 0x40000000
	WS_EX_TOPMOST       = 0x00000008
	WS_EX_DLGMODALFRAME = 0x00000001
	SW_SHOW             = 5
	WM_DESTROY          = 0x0002
	WM_CLOSE            = 0x0010
	WM_SETFONT          = 0x0030
	SS_CENTER           = 0x00000001
	SM_CXSCREEN         = 0
	SM_CYSCREEN         = 1
	MB_RETRYCANCEL      = 0x00000005
	MB_ICONWARNING      = 0x00000030
	IDRETRY             = 4
	COLOR_WINDOW        = 5
)

type WNDCLASSEX struct {
	CbSize        uint32
	Style         uint32
	LpfnWndProc   uintptr
	CbClsExtra    int32
	CbWndExtra    int32
	HInstance     syscall.Handle
	HIcon         syscall.Handle
	HCursor       syscall.Handle
	HbrBackground syscall.Handle
	LpszMenuName  *uint16
	LpszClassName *uint16
	HIconSm       syscall.Handle
}

type POINT struct {
	X, Y int32
}

type MSG struct {
	Hwnd     syscall.Handle
	Message  uint32
	WParam   uintptr
	LParam   uintptr
	Time     uint32
	Pt       POINT
	LPrivate uint32
}

const targetURL = "http://127.0.0.1:49374/?auth_token=educamadrid"

func checkOpenCode() bool {
	client := http.Client{Timeout: 1200 * time.Millisecond}
	resp, err := client.Get("http://127.0.0.1:49374/")
	if err != nil {
		return false
	}
	_ = resp.Body.Close()
	return resp.StatusCode == 200 || resp.StatusCode == 401
}

func MessageBox(title, text string, style uint) int {
	t, _ := syscall.UTF16PtrFromString(title)
	m, _ := syscall.UTF16PtrFromString(text)
	ret, _, _ := procMessageBoxW.Call(0, uintptr(unsafe.Pointer(m)), uintptr(unsafe.Pointer(t)), uintptr(style))
	return int(ret)
}

func findBrowser() (string, []string) {
	localAppData := os.Getenv("LOCALAPPDATA")
	profileDir := filepath.Join(localAppData, "OpenCodeEducaMadrid", "profile")

	progFiles86 := os.Getenv("ProgramFiles(x86)")
	progFiles := os.Getenv("ProgramFiles")

	candidates := []string{
		filepath.Join(progFiles86, "Microsoft", "Edge", "Application", "msedge.exe"),
		filepath.Join(progFiles, "Microsoft", "Edge", "Application", "msedge.exe"),
		filepath.Join(localAppData, "Microsoft", "Edge", "Application", "msedge.exe"),
		filepath.Join(progFiles, "Google", "Chrome", "Application", "chrome.exe"),
		filepath.Join(progFiles86, "Google", "Chrome", "Application", "chrome.exe"),
		filepath.Join(localAppData, "Google", "Chrome", "Application", "chrome.exe"),
		filepath.Join(progFiles, "BraveSoftware", "Brave-Browser", "Application", "brave.exe"),
		filepath.Join(localAppData, "BraveSoftware", "Brave-Browser", "Application", "brave.exe"),
	}

	for _, c := range candidates {
		if c != "" {
			if _, err := os.Stat(c); err == nil {
				args := []string{
					fmt.Sprintf("--app=%s", targetURL),
					fmt.Sprintf("--user-data-dir=%s", profileDir),
					"--window-size=1400,900",
				}
				return c, args
			}
		}
	}

	return "cmd.exe", []string{"/c", "start", "", targetURL}
}

func launchBrowser() error {
	bin, args := findBrowser()
	cmd := exec.Command(bin, args...)
	return cmd.Start()
}

func wndProc(hwnd syscall.Handle, msg uint32, wParam, lParam uintptr) uintptr {
	switch msg {
	case WM_CLOSE:
		procDestroyWindow.Call(uintptr(hwnd))
		return 0
	case WM_DESTROY:
		procPostQuitMessage.Call(0)
		return 0
	}
	ret, _, _ := procDefWindowProcW.Call(uintptr(hwnd), uintptr(msg), wParam, lParam)
	return ret
}

func showSplashAndConnect() bool {
	runtime.LockOSThread()
	defer runtime.UnlockOSThread()

	hInst, _, _ := procGetModuleHandleW.Call(0)
	className, _ := syscall.UTF16PtrFromString("OpenCodeEducaMadridSplash")
	wndTitle, _ := syscall.UTF16PtrFromString("OpenCode v2 - EducaMadrid")

	var wc WNDCLASSEX
	wc.CbSize = uint32(unsafe.Sizeof(wc))
	wc.Style = 0
	wc.LpfnWndProc = syscall.NewCallback(wndProc)
	wc.HInstance = syscall.Handle(hInst)
	wc.HbrBackground = syscall.Handle(COLOR_WINDOW + 1)
	wc.LpszClassName = className

	procRegisterClassExW.Call(uintptr(unsafe.Pointer(&wc)))

	width := int32(480)
	height := int32(200)
	scrW, _, _ := procGetSystemMetrics.Call(SM_CXSCREEN)
	scrH, _, _ := procGetSystemMetrics.Call(SM_CYSCREEN)
	x := (int32(scrW) - width) / 2
	y := (int32(scrH) - height) / 2

	style := WS_OVERLAPPED | WS_CAPTION | WS_SYSMENU | WS_MINIMIZEBOX | WS_VISIBLE
	exStyle := WS_EX_TOPMOST | WS_EX_DLGMODALFRAME

	hwnd, _, _ := procCreateWindowExW.Call(
		uintptr(exStyle),
		uintptr(unsafe.Pointer(className)),
		uintptr(unsafe.Pointer(wndTitle)),
		uintptr(style),
		uintptr(x),
		uintptr(y),
		uintptr(width),
		uintptr(height),
		0, 0, hInst, 0,
	)

	if hwnd == 0 {
		return false
	}

	staticClass, _ := syscall.UTF16PtrFromString("STATIC")
	titleText, _ := syscall.UTF16PtrFromString("OpenCode - Aula Virtual EducaMadrid")
	msgText, _ := syscall.UTF16PtrFromString("Conectando con la Máquina Virtual...")
	statusText, _ := syscall.UTF16PtrFromString("Esperando a que el servicio OpenCode esté listo...")

	fontTitle, _, _ := procCreateFontW.Call(22, 0, 0, 0, 700, 0, 0, 0, 0, 0, 0, 0, 0, uintptr(unsafe.Pointer(syscall.StringToUTF16Ptr("Segoe UI"))))
	fontNormal, _, _ := procCreateFontW.Call(16, 0, 0, 0, 400, 0, 0, 0, 0, 0, 0, 0, 0, uintptr(unsafe.Pointer(syscall.StringToUTF16Ptr("Segoe UI"))))

	lblTitle, _, _ := procCreateWindowExW.Call(
		0, uintptr(unsafe.Pointer(staticClass)), uintptr(unsafe.Pointer(titleText)),
		WS_CHILD|WS_VISIBLE|SS_CENTER,
		10, 22, 440, 28, hwnd, 101, hInst, 0,
	)
	if fontTitle != 0 {
		procSendMessageW.Call(lblTitle, WM_SETFONT, fontTitle, 1)
	}

	lblMsg, _, _ := procCreateWindowExW.Call(
		0, uintptr(unsafe.Pointer(staticClass)), uintptr(unsafe.Pointer(msgText)),
		WS_CHILD|WS_VISIBLE|SS_CENTER,
		10, 64, 440, 24, hwnd, 102, hInst, 0,
	)
	if fontNormal != 0 {
		procSendMessageW.Call(lblMsg, WM_SETFONT, fontNormal, 1)
	}

	lblStatus, _, _ := procCreateWindowExW.Call(
		0, uintptr(unsafe.Pointer(staticClass)), uintptr(unsafe.Pointer(statusText)),
		WS_CHILD|WS_VISIBLE|SS_CENTER,
		10, 105, 440, 24, hwnd, 103, hInst, 0,
	)
	if fontNormal != 0 {
		procSendMessageW.Call(lblStatus, WM_SETFONT, fontNormal, 1)
	}

	procShowWindow.Call(hwnd, SW_SHOW)
	procUpdateWindow.Call(hwnd)

	var connected int32
	var done int32

	go func() {
		for i := 1; i <= 50; i++ {
			if atomic.LoadInt32(&done) == 1 {
				return
			}
			if checkOpenCode() {
				atomic.StoreInt32(&connected, 1)
				txt, _ := syscall.UTF16PtrFromString("¡Conexión establecida! Abriendo OpenCode...")
				procSetWindowTextW.Call(lblStatus, uintptr(unsafe.Pointer(txt)))
				time.Sleep(350 * time.Millisecond)
				procPostMessageW.Call(hwnd, WM_CLOSE, 0, 0)
				return
			}
			txt, _ := syscall.UTF16PtrFromString(fmt.Sprintf("Esperando a la Máquina Virtual (intento %d de 50)...", i))
			procSetWindowTextW.Call(lblStatus, uintptr(unsafe.Pointer(txt)))
			time.Sleep(1000 * time.Millisecond)
		}
		procPostMessageW.Call(hwnd, WM_CLOSE, 0, 0)
	}()

	var msg MSG
	for {
		ret, _, _ := procGetMessageW.Call(uintptr(unsafe.Pointer(&msg)), 0, 0, 0)
		if int32(ret) <= 0 {
			break
		}
		procTranslateMessage.Call(uintptr(unsafe.Pointer(&msg)))
		procDispatchMessageW.Call(uintptr(unsafe.Pointer(&msg)))
	}

	atomic.StoreInt32(&done, 1)
	return atomic.LoadInt32(&connected) == 1
}

func main() {
	if checkOpenCode() {
		_ = launchBrowser()
		return
	}

	for {
		if showSplashAndConnect() {
			_ = launchBrowser()
			return
		}

		res := MessageBox(
			"OpenCode - EducaMadrid",
			"No se ha podido conectar con OpenCode en la Máquina Virtual.\n\n"+
				"Por favor, comprueba que:\n"+
				"1. La máquina 'ArchLinux-EducaMadrid' está iniciada en VirtualBox.\n"+
				"2. El puerto NAT 49374 está activo en la configuración de red.\n\n"+
				"¿Deseas volver a intentar la conexión?",
			MB_RETRYCANCEL|MB_ICONWARNING,
		)
		if res != IDRETRY {
			return
		}
	}
}
