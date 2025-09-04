package main

import (
	"encoding/hex"
	"fmt"
	"runtime"
	"sync"

	"github.com/wealdtech/go-merkletree/keccak256"
)

func getSelector(signature string) string {
	fullHash := keccak256.New().Hash([]byte(signature))
	return hex.EncodeToString(fullHash[:4])
}

const (
	chars     = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
	startLen  = 1
	maxLen    = 20 // you can increase this
	targetSig = "solve()"
)

func pow(base, exp int) int {
	result := 1
	for i := 0; i < exp; i++ {
		result *= base
	}
	return result
}

// Converts a numeric index to a string based on 'chars' set
func indexToString(index, length int) string {
	b := make([]byte, length)
	for i := length - 1; i >= 0; i-- {
		b[i] = chars[index%len(chars)]
		index /= len(chars)
	}
	return string(b)
}

func worker(start, end, length int, targetSelector string, found *bool, foundLock *sync.Mutex, wg *sync.WaitGroup) {
	defer wg.Done()

	for i := start; i < end; i++ {
		foundLock.Lock()
		if *found {
			foundLock.Unlock()
			return
		}
		foundLock.Unlock()

		candidateBase := indexToString(i, length)
		candidate := candidateBase + "()"

		if candidate != targetSig {
			sel := getSelector(candidate)
			if sel == targetSelector {
				fmt.Printf("\nCollision found!\n")
				fmt.Printf("%s -> %s\n", targetSig, targetSelector)
				fmt.Printf("%s -> %s\n", candidate, sel)
				foundLock.Lock()
				*found = true
				foundLock.Unlock()
				return
			}
		}
	}
}

func main() {
	targetSelector := getSelector(targetSig)
	fmt.Printf("Target selector for %s: %s\n", targetSig, targetSelector)

	var found bool
	var foundLock sync.Mutex

	numCPU := runtime.NumCPU()
	fmt.Printf("Using %d CPU cores\n", numCPU)

	for length := startLen; length <= maxLen; length++ {
		total := pow(len(chars), length)
		chunkSize := total / numCPU
		if chunkSize == 0 {
			chunkSize = total // fallback for small spaces
		}

		fmt.Printf("Searching length %d with total %d candidates...\n", length, total)

		var wg sync.WaitGroup
		for i := 0; i < numCPU; i++ {
			start := i * chunkSize
			end := start + chunkSize
			if i == numCPU-1 {
				end = total
			}

			wg.Add(1)
			go worker(start, end, length, targetSelector, &found, &foundLock, &wg)
		}

		wg.Wait()

		if found {
			break
		}
	}

	if !found {
		fmt.Println("No collision found.")
	}
}
