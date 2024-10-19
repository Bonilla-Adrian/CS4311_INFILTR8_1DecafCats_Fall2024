class IP {
    //SRS does not specify what IP version so we will only accept ipv4 addresses
    constructor(ip, selected = false) {         
        this.ip = ip;          
        this.selected = selected;
    }

    toggleSelected() {
        this.selected = !this.selected;
    }

    getDescription() {
        return `IP ID: ${this.id}, IP Address: ${this.ip}, Selected: ${this.selected}`;
    }
}

export default IP;