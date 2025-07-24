// app/static/script.js

document.addEventListener('DOMContentLoaded', () => {
    const shortenForm = document.getElementById('shortenForm');
    const originalUrlInput = document.getElementById('originalUrl');
    const resultDiv = document.getElementById('result');
    const refreshUrlsButton = document.getElementById('refreshUrls');
    const urlList = document.getElementById('urlList');
    const noUrlsMessage = document.getElementById('noUrlsMessage');

    const messageBox = document.getElementById('messageBox');
    const messageText = document.getElementById('messageText');
    const closeMessageBox = document.getElementById('closeMessageBox');

    /**
     * Shows a custom message box.
     * @param {string} message - The message to display.
     */
    function showMessageBox(message) {
        messageText.textContent = message;
        messageBox.classList.remove('hidden');
    }

    // Event listener to close the message box
    closeMessageBox.addEventListener('click', () => {
        messageBox.classList.add('hidden');
    });

    /**
     * Fetches and displays the list of all shortened URLs.
     */
    async function fetchAndDisplayUrls() {
        try {
            const response = await fetch('/api/urls');
            if (!response.ok) {
                const errorData = await response.json();
                showMessageBox(`Error fetching URLs: ${errorData.error || response.statusText}`);
                return;
            }
            const urls = await response.json();
            urlList.innerHTML = ''; // Clear existing list

            if (urls.length === 0) {
                noUrlsMessage.classList.remove('hidden');
            } else {
                noUrlsMessage.classList.add('hidden');
                urls.forEach(url => {
                    const listItem = document.createElement('li');
                    listItem.className = 'bg-gray-50 p-2 rounded-md flex flex-col sm:flex-row sm:justify-between sm:items-center text-sm break-all';
                    listItem.innerHTML = `
                        <div class="mb-1 sm:mb-0">
                            <span class="font-semibold text-blue-700">Original:</span> <a href="${url.original_url}" target="_blank" class="hover:underline text-blue-600">${url.original_url}</a>
                        </div>
                        <div class="mt-1 sm:mt-0">
                            <span class="font-semibold text-green-700">Short:</span> <a href="${url.short_url}" target="_blank" class="hover:underline text-green-600">${url.short_url}</a>
                            <button class="copy-button ml-2 px-2 py-1 bg-gray-200 text-gray-700 rounded-md text-xs hover:bg-gray-300" data-url="${url.short_url}">Copy</button>
                        </div>
                    `;
                    urlList.appendChild(listItem);
                });

                // Attach event listeners to copy buttons
                document.querySelectorAll('.copy-button').forEach(button => {
                    button.addEventListener('click', (event) => {
                        const urlToCopy = event.target.dataset.url;
                        copyToClipboard(urlToCopy);
                    });
                });
            }
        } catch (error) {
            console.error('Failed to fetch URLs:', error);
            showMessageBox('Failed to fetch URLs. Please check your connection or server logs.');
        }
    }

    /**
     * Copies text to the clipboard using document.execCommand.
     * @param {string} text - The text to copy.
     */
    function copyToClipboard(text) {
        const textarea = document.createElement('textarea');
        textarea.value = text;
        textarea.style.position = 'fixed'; // Avoid scrolling to bottom
        document.body.appendChild(textarea);
        textarea.focus();
        textarea.select();
        try {
            document.execCommand('copy');
            showMessageBox('Short URL copied to clipboard!');
        } catch (err) {
            console.error('Failed to copy text: ', err);
            showMessageBox('Failed to copy URL. Please copy manually.');
        }
        document.body.removeChild(textarea);
    }


    // Handle form submission for shortening URLs
    shortenForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        resultDiv.textContent = 'Shortening URL...';
        resultDiv.className = 'mt-4 text-center text-gray-700 animate-pulse';

        const originalUrl = originalUrlInput.value;

        try {
            const response = await fetch('/api/shorten', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ original_url: originalUrl }),
            });

            const data = await response.json();

            if (response.ok) {
                resultDiv.innerHTML = `
                    <p class="text-green-600 font-semibold mb-2">URL shortened successfully!</p>
                    <p>Original: <a href="${data.original_url}" target="_blank" class="text-blue-600 hover:underline break-all">${data.original_url}</a></p>
                    <p class="mt-1">Short: <a href="${data.short_url}" target="_blank" class="text-green-600 font-bold hover:underline break-all">${data.short_url}</a></p>
                    <button class="copy-button mt-3 px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 transition duration-300" data-url="${data.short_url}">Copy Short URL</button>
                `;
                resultDiv.className = 'mt-4 text-center text-gray-700'; // Remove pulse
                // Attach copy button listener immediately after rendering
                document.querySelector('#result .copy-button').addEventListener('click', (e) => {
                    copyToClipboard(e.target.dataset.url);
                });
                fetchAndDisplayUrls(); // Refresh the list of URLs
            } else {
                resultDiv.textContent = `Error: ${data.error || 'Unknown error'}`;
                resultDiv.className = 'mt-4 text-center text-red-600 font-semibold'; // Error styling
            }
        } catch (error) {
            console.error('Error:', error);
            resultDiv.textContent = 'An error occurred. Please try again.';
            resultDiv.className = 'mt-4 text-center text-red-600 font-semibold';
        }
    });

    // Refresh button event listener
    refreshUrlsButton.addEventListener('click', fetchAndDisplayUrls);

    // Initial load of URLs when the page loads
    fetchAndDisplayUrls();
});
