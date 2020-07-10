

socket_data_cache = {}
sentinel = object()

# Build string for showing in socket label
def bNCGetSocketInfo(socket):
    """returns string to show in socket label"""
    global socket_data_cache
    ng = socket.id_data.tree_id

    if socket.is_output:
        s_id = socket.socket_id
    elif socket.is_linked:
        other = socket.other
        if other and hasattr(other, 'socket_id'):
            s_id = other.socket_id
        else:
            return ''
    else:
        return ''
    if ng in socket_data_cache:
        if s_id in socket_data_cache[ng]:
            data = socket_data_cache[ng][s_id]
            if data:
                return str(len(data))
    return ''

def bNCForgetSocket(socket):
    """deletes socket data from cache"""
    global socket_data_cache
    if data_structure.DEBUG_MODE:
        if not socket.is_output:
            warning(f"{socket.node.name} forgetting input socket: {socket.name}")
        if not socket.is_linked:
            warning(f"{socket.node.name} forgetting unconncted socket: {socket.name}")
    s_id = socket.socket_id
    s_ng = socket.id_data.tree_id
    try:
        socket_data_cache[s_ng].pop(s_id, None)
    except KeyError:
        print("it was never there")

def bNCSetSocket(socket, out):
    """sets socket data for socket"""
    global socket_data_cache
    if data_structure.DEBUG_MODE:
        if not socket.is_output:
            warning(f"{socket.node.name} setting input socket: {socket.name}")
        if not socket.is_linked:
            warning(f"{socket.node.name} setting unconncted socket: {socket.name}")
    s_id = socket.socket_id
    s_ng = socket.id_data.tree_id
    if s_ng not in socket_data_cache:
        socket_data_cache[s_ng] = {}
    socket_data_cache[s_ng][s_id] = out


def bNCGetSocket(socket, deepcopy=True):
    """gets socket data from socket,
    if deep copy is True a deep copy is make_dep_dict,
    to increase performance if the node doesn't mutate input
    set to False and increase performance substanstilly
    """
    global socket_data_cache
    if socket.is_linked:
        other = socket.other
        s_id = other.socket_id
        s_ng = other.id_data.tree_id
        if s_ng not in socket_data_cache:
            raise LookupError
        if s_id in socket_data_cache[s_ng]:
            out = socket_data_cache[s_ng][s_id]
            if deepcopy:
                return sv_deep_copy(out)
            else:
                return out
        else:
            if data_structure.DEBUG_MODE:
                debug(f"cache miss: {socket.node.name} -> {socket.name} from: {other.node.name} -> {other.name}")
            raise SvNoDataError(socket, msg="not found in socket_data_cache")
    # not linked
    raise SvNoDataError(socket)

class bNCNoDataError(LookupError):
    def __init__(self, socket=None, node=None, msg=None):
        
        self.extra_message = msg if msg else ""

        if node is None and socket is not None:
            node = socket.node
        self.node = node
        self.socket = socket

        super(LookupError, self).__init__(self.get_message())

    def get_message(self):
        if self.extra_message:
            return f"node {self.socket.node.name} (socket {self.socket.name}) {self.extra_message}"
        if not self.node and not self.socket:
            return "SvNoDataError"
        else:
            return f"No data passed into socket '{self.socket.name}'"
    
    def __repr__(self):
        return self.get_message()
    
    def __str__(self):
        return repr(self)

    def __unicode__(self):
        return repr(self)
    
    def __format__(self, spec):
        return repr(self)

def get_output_socket_data(node, output_socket_name):
    """
    This method is intended to usage in internal tests mainly.
    Get data that the node has written to the output socket.
    Raises SvNoDataError if it hasn't written any.
    """

    global socket_data_cache

    tree_name = node.id_data.tree_id
    socket = node.outputs[output_socket_name]
    socket_id = socket.socket_id
    if tree_name not in socket_data_cache:
        raise bNCNoDataError()
    if socket_id in socket_data_cache[tree_name]:
        return socket_data_cache[tree_name][socket_id]
    else:
        raise bNCNoDataError(socket)

def reset_socket_cache(ng):
    """
    Reset socket cache either for node group.
    """
    global socket_data_cache
    socket_data_cache[ng.tree_id] = {}

def clear_all_socket_cache():
    """
    Reset socket cache for all node-trees.
    """
    global socket_data_cache
    socket_data_cache.clear()
