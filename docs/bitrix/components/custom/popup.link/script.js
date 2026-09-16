(function() {
    if (window.BX && BX.PopupWindowManager) {
        BX.ready(function() {
            document.addEventListener('click', function(e) {
                var target = e.target.closest('[data-popup-id]');
                if (!target) return;
                e.preventDefault();

                var popupId = target.getAttribute('data-popup-id');
                if (!popupId) return;

                // Загружаем контент через AJAX
                BX.ajax({
                    url: '/bitrix/tools/custom.popup/ajax.php?popup_id=' + popupId,
                    method: 'GET',
                    dataType: 'json',
                    onsuccess: function(response) {
                        if (response.error) {
                            console.error(response.error);
                            return;
                        }
                        var popupContent = BX.create('div', { html: response.content });
                        var popup = BX.PopupWindowManager.create(
                            'custom-popup-' + popupId,
                            null,
                            {
                                content: popupContent,
                                closeIcon: true,
                                titleBar: response.title || '',
                                zIndex: 10000,
                                autoHide: true,
                                draggable: true,
                                overlay: { opacity: 20 },
                                buttons: [
                                    BX.create('span', {
                                        text: 'Закрыть',
                                        props: { className: 'btn btn-default' },
                                        events: { click: function() { popup.close(); } }
                                    })
                                ]
                            }
                        );
                        popup.show();
                    },
                    onfailure: function() {
                        console.error('Ошибка загрузки окна');
                    }
                });
            });
        });
    }
})();