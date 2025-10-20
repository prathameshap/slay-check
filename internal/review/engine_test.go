package review

import (
	"testing"

	"github.com/slay-check/slay-check/internal/config"
	"github.com/slay-check/slay-check/internal/github"
)

func TestDetectLanguage(t *testing.T) {
	cfg := config.DefaultConfig()
	engine := &Engine{config: cfg}

	tests := []struct {
		name     string
		filename string
		want     string
	}{
		{
			name:     "Go file",
			filename: "main.go",
			want:     "go",
		},
		{
			name:     "JavaScript file",
			filename: "script.js",
			want:     "javascript",
		},
		{
			name:     "TypeScript file",
			filename: "app.ts",
			want:     "typescript",
		},
		{
			name:     "Python file",
			filename: "main.py",
			want:     "python",
		},
		{
			name:     "Java file",
			filename: "App.java",
			want:     "java",
		},
		{
			name:     "Unknown file",
			filename: "unknown.xyz",
			want:     "text",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := engine.detectLanguage(tt.filename)
			if got != tt.want {
				t.Errorf("detectLanguage() = %v, want %v", got, tt.want)
			}
		})
	}
}

func TestExtractCodeFromPatch(t *testing.T) {
	cfg := config.DefaultConfig()
	engine := &Engine{config: cfg}

	tests := []struct {
		name  string
		patch string
		want  string
	}{
		{
			name:  "simple patch",
			patch: "+func main() {\n+    fmt.Println(\"Hello\")\n+}",
			want:  "func main() {\n    fmt.Println(\"Hello\")\n}",
		},
		{
			name:  "patch with context",
			patch: "@@ -1,3 +1,3 @@\n func main() {\n-    fmt.Println(\"Old\")\n+    fmt.Println(\"New\")\n }",
			want:  "    fmt.Println(\"New\")",
		},
		{
			name:  "empty patch",
			patch: "",
			want:  "",
		},
		{
			name:  "patch without additions",
			patch: "-func main() {\n-    fmt.Println(\"Hello\")\n-}",
			want:  "",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := engine.extractCodeFromPatch(tt.patch)
			if got != tt.want {
				t.Errorf("extractCodeFromPatch() = %v, want %v", got, tt.want)
			}
		})
	}
}

func TestShouldExcludeFile(t *testing.T) {
	cfg := config.DefaultConfig()
	cfg.ExcludePatterns = []string{"*.md", "*.txt", "vendor/*", "testdata/*"}
	engine := &Engine{config: cfg}

	tests := []struct {
		name     string
		filename string
		want     bool
	}{
		{
			name:     "markdown file",
			filename: "README.md",
			want:     true,
		},
		{
			name:     "text file",
			filename: "notes.txt",
			want:     true,
		},
		{
			name:     "vendor file",
			filename: "vendor/github.com/pkg/errors/errors.go",
			want:     true,
		},
		{
			name:     "testdata file",
			filename: "testdata/sample.json",
			want:     true,
		},
		{
			name:     "Go source file",
			filename: "main.go",
			want:     false,
		},
		{
			name:     "JavaScript file",
			filename: "app.js",
			want:     false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := engine.shouldExcludeFile(tt.filename)
			if got != tt.want {
				t.Errorf("shouldExcludeFile() = %v, want %v", got, tt.want)
			}
		})
	}
}

func TestFilterFiles(t *testing.T) {
	cfg := config.DefaultConfig()
	cfg.MaxFileSize = 100
	cfg.MaxFilesPerPR = 3
	cfg.ExcludePatterns = []string{"*.md"}
	engine := &Engine{config: cfg}

	files := []github.PullRequestFile{
		{
			Filename: "main.go",
			Status:   "modified",
			Changes:  50,
		},
		{
			Filename: "README.md",
			Status:   "modified",
			Changes:  10,
		},
		{
			Filename: "large.go",
			Status:   "modified",
			Changes:  150, // Exceeds max file size
		},
		{
			Filename: "deleted.go",
			Status:   "removed",
			Changes:  20,
		},
		{
			Filename: "extra.go",
			Status:   "modified",
			Changes:  30,
		},
	}

	filtered := engine.filterFiles(files)

	// Should exclude: README.md (pattern), large.go (size), deleted.go (removed)
	// Should include: main.go, extra.go (but limited to max_files_per_pr)
	expectedCount := 2 // main.go and extra.go, but limited by max_files_per_pr
	if len(filtered) != expectedCount {
		t.Errorf("Expected %d filtered files, got %d", expectedCount, len(filtered))
	}

	// Check that the remaining files are the expected ones
	filenames := make([]string, len(filtered))
	for i, file := range filtered {
		filenames[i] = file.Filename
	}

	expectedFiles := []string{"main.go", "extra.go"}
	for i, expected := range expectedFiles {
		if i < len(filenames) && filenames[i] != expected {
			t.Errorf("Expected file %s at position %d, got %s", expected, i, filenames[i])
		}
	}
}
