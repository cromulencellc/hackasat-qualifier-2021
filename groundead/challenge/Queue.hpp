#include <stdio.h>
#include <netdb.h>
#include <netinet/in.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <fcntl.h> // for open
#include <unistd.h> // for close
#include <threads.h>
#include <iostream>
#include <iomanip>
#include <sstream>
#include <queue>

#define QUEUE_SIZE 2048

// The Queue class is used to simulate the sending of CCSDS packets from the ground station
// to the satellite and the receiving of CCSDS packets sent from the satellite to the ground
// station. When a packet is added to the Queue, the packet can be thought of as immediately
// being sent from the ground station to the satellite. Similarly, when a packet is removed
// from the Queue, it can be thought of as having arrived at the ground station from the 
// satellite. 
class Queue 
{
private:
  // uint8_t items[QUEUE_SIZE], front, rear;

  int8_t items[QUEUE_SIZE];
  int8_t front;
  int8_t rear;

  // int8_t value;

public:
  Queue() 
  {
    front = -1;
    rear = -1;
  }

  // Check if the queue is full
  bool isFull() 
  {
    if (front == 0 && rear == QUEUE_SIZE - 1) 
    {
      return true;
    }

    if (front == rear + 1) 
    {
      return true;
    }

    return false;
  }

  // Check if the queue is empty.
  bool isEmpty() 
  {
    // std::cout << "JEFF - front is: " << front << std::endl;

    // printf("JEFF - the value of front is: %d\n", front);
    // fflush(stdout);

    if (front == -1)
    {
      // std::cout << "QUEUE - made it to point 2. JEFF" << std::endl;

      return true;
    }
    else
    {
      // std::cout << "QUEUE - made it to point 3. JEFF" << std::endl;

      return false;
    }
  }

  // Adding an element.
  void enQueue(uint8_t element) 
  {
    if (isFull()) 
    {
      std::cout << std::endl << "Queue is full" << std::endl;
    } 
    else 
    {
      if (front == -1)
      {
          front = 0;
      }

      rear = (rear + 1) % QUEUE_SIZE;

      items[rear] = element;
    }
  }

  // Removing an element
  int deQueue() 
  {
    uint8_t element;

    // std::cout << "QUEUE - made it to point 1. JEFF" << std::endl;

    if (isEmpty()) 
    {
      std::cout << std::endl << "Queue is empty" << std::endl;
      return (-1);
    } 
    else 
    {
      element = items[front];

      if (front == rear) 
      {
        front = -1;
        rear = -1;
      }

      // Q has only one element,
      // so we reset the queue after deleting it.

      else 
      {
        front = (front + 1) % QUEUE_SIZE;
      }

      return (element);
    }
  }

  void display() 
  {
    // Function to display status of Circular Queue

    int i;

    if (isEmpty()) 
    {
      std::cout << std::endl << "Empty Queue" << std::endl;
    } 
    else 
    {
      std::cout << std::endl << "Front -> " << front << std::endl;

      std::cout << std::endl << "Items -> ";

      for (i = front; i != rear; i = (i + 1) % QUEUE_SIZE)
      {
        std::cout << items[i] << " ";
      }

      std::cout << items[i];

      std::cout << std::endl << "Rear -> " << rear;
    }
  }
};
