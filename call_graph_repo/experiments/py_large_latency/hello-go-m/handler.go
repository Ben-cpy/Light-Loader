package function

import (
	"fmt"
)

func Handle(req []byte) string {
	return fmt.Sprintf("Hello from Go with large module!")
}
