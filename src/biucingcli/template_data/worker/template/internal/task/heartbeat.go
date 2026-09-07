package task

import (
	"context"
	"fmt"
	"time"
)

type HeartbeatTask struct {
	workerName string
}

func NewHeartbeatTask(workerName string) *HeartbeatTask {
	return &HeartbeatTask{workerName: workerName}
}

func (task *HeartbeatTask) Execute(context.Context) (string, error) {
	return fmt.Sprintf("%s heartbeat completed at %s", task.workerName, time.Now().UTC().Format(time.RFC3339)), nil
}
