- Special code for two-pin nets
- Take a snapshot when a move make **negative** gain.
- Snapshot in the form of "interface"

```python
# initialization
def initialization():
    totalgain = 0

    while not self.gainbucket.is_empty():
        # take the gainmax with v from gainbucket
        gainmax = self.gainbucket.get_max()
        v = self.gainbucket.popleft()
        self.waitinglist.append(v)

        # check if the move of v can satisfied, makebetter, or notsatisfied
        validcheck = self.validator(v)
        if validcheck == notsatisfied:
            continue

        move v
        update v and its neigbours (even they are in waitinglist)
        totalgain += gainmax
        put neigbours to bucket

        if validcheck == satisfied:
            self.totalcost = totalgain
            # totalgain = 0 # reset to zero
            break
```


# Optimization

```python
def optimization():
    totalgain = 0
    deferedsnapshot = True
    while not self.gainbucket.is_empty():
        # take the gainmax with v from gainbucket
        gainmax = self.gainbucket.get_max()
        v = self.gainbucket.popleft()
        self.waitinglist.append(v)

        # check if the move of v can satisfied or notsatisfied
        satisfiedOK = self.constraintcheck(v)

        if not satisfiedOK:
            continue

        if self.totalgain >= 0:
            if totalgain < -gainmax:
                # become down turn 
                take a snapshot before move
                deferedsnapshot = False

        move v
        update v and its neigbours (even they are in waitinglist)
        totalgain += gainmax

        if totalgain > 0:
            self.totalcost -= totalgain
            totalgain = 0 # reset to zero
            deferedsnapshot = True
            put all neigbours to bucket
        else:
            put only positive gain neigbours to bucket
```
