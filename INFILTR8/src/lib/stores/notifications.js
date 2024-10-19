// src/lib/stores/notifications.js
import { writable } from 'svelte/store';

export const notifications = writable([]);

let currentPage = 0;
const pageSize = 20;

// Fetch the most recent notifications from Neo4j
export async function loadNotificationsFromDB(username) {
    const skip = currentPage * pageSize;
    const dbNotifications = await getUserNotifications(username, skip, pageSize); // Fetch with pagination from Neo4j
    notifications.update(n => [...n, ...dbNotifications.map(notification => ({
        ...notification,
        isNew: false, // Mark notifications from the DB as not new
        isPermanent: true // Ensure all notifications from the DB are marked as permanent
    }))]);
    currentPage++; // Increment for pagination
}

// Add new notification (distinguish between temporary and permanent)
export function addNewNotification(notification) {
    notifications.update(n => [...n, {
        ...notification,
        isNew: true, // Mark as new (to be shown in the toast)
        isPermanent: notification.isPermanent ?? false // Default to false if not specified
    }]);
    console.log('New notification:', notification);
    
    // If it's permanent, sync it with the backend
    if (notification.isPermanent) {
        writeNotificationToBackend(notification); // A function to sync with the backend
    }
}

// Mark notification as old (after being shown in Toast, but no removal)
export function markNotificationAsOld(id) {
    notifications.update(n => n.map(notification =>
        notification.id === id ? { ...notification, isNew: false } : notification
    ));
}

// Remove notification (only temporary removal is handled in the notification section)
export function removeNotificationFromBackend(id) {
    console.log("Removing from backend:", id);
    // Your logic here to remove from the Neo4j backend (this will be handled in the future notification section)
}

// Dummy function to simulate writing a permanent notification to the backend
async function writeNotificationToBackend(notification) {
    console.log("Writing to backend:", notification);
    // Your logic here to write to the Neo4j backend
}
