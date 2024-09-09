def setup(db: og.Database):
    state = db.internal_state

def cleanup(db: og.Database):
    pass

def compute(db: og.Database):
    state = db.internal_state
    orient = db.inputs.orient
    # orient is float[4] type data, print it with human readable text
    print(f"orient: {orient}")

    return True
