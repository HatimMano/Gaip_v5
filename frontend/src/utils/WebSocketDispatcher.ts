type Message = {
  type?: string; 
  data?: any;
  state?: any; 
};

interface DispatcherHandlers {
  state?: (data: any) => void;
  config?: (data: any) => void;
  error?: (data: any) => void;
}

class WebSocketDispatcher {
  private handlers: DispatcherHandlers = {};
  private setState: ((state: any) => void) | null = null;

  registerHandler(type: string, handler: (data: any) => void) {
    this.handlers[type as keyof DispatcherHandlers] = handler;
  }

  registerStateHandler(setState: (state: any) => void) {
    this.setState = setState;
  }

  dispatch(message: Message) {
    let { type, data, state } = message;

    if (!type && state) {
      type = "state";
      data = state;
    }

    const handler = this.handlers[type as keyof DispatcherHandlers];

    if (handler) {
      handler(data);
    } else if (type === "state" && this.setState) {
      this.setState(data);
    } else {
      console.warn(`🚨 Aucun handler trouvé pour le type de message: ${type}`);
    }
  }
}

const dispatcher = new WebSocketDispatcher();
export default dispatcher;
