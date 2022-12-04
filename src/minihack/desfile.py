def gen_desfile(all_visible=False):
    header = f"""
    LEVEL: "mylevel"
    
    {"FLAGS: premapped" if all_visible else ""}
    """
    body = """
    ROOM: "ordinary" , lit, random, random, random {
        OBJECT:('(', "skeleton key"), random
    }
    ROOM: "ordinary" , lit, random, random, random {
        OBJECT:('(', "skeleton key"), random
    }
    ROOM: "ordinary" , lit, random, random, random {
        OBJECT:('(', "skeleton key"), random
    }
    ROOM: "ordinary" , lit, random, random, random {
        STAIR: random, down
    }
    
    RANDOM_CORRIDORS
    """
    return f"{header}\n{body}"
