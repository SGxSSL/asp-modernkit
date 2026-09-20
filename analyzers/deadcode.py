def analyze(inventory, routes, includes_map):
    """
    Identify deadcode by traversing the include graph starting from routes.
    
    Args:
        inventory (list): List of all file paths.
        routes (list): List of files identified as routes.
        includes_map (dict): Map of file -> list of files it includes.
        
    Returns:
        list: List of deadcode file paths.
    """
    visited = set()
    queue = list(routes)
    while queue:
        current = queue.pop(0)
        if current not in visited:
            visited.add(current)
            if current in includes_map:
                queue.extend(includes_map[current])
                
    deadcode = []
    for file in inventory:
        if file.lower().endswith(('.asp', '.inc')) and file not in visited:
            deadcode.append(file)
    return deadcode
