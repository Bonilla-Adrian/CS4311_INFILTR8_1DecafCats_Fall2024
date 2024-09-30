export class SystemInfo {
    constructor() {
        this.updateTimestamp();
    }

    updateTimestamp() {
        const currentDate = new Date();
        this.timestamp = `[ ${currentDate.getMonth() + 1}/${
            currentDate.getDate()
        }/${currentDate.getFullYear()} @ ${currentDate.getHours()}:${
            currentDate.getMinutes()
        }:${currentDate.getSeconds()}]`;
    }

    getFormattedDate() {
        const currentDate = new Date();
        return `${currentDate.getFullYear()}-${currentDate.getMonth() + 1}-${currentDate.getDate()}`;
    }

    getCurrentTimestamp() {
        this.updateTimestamp();
        return this.timestamp;
    }
}
