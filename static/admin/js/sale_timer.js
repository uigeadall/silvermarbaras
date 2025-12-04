(function($) {
    'use strict';
    
    // Function to check if Sale category is selected
    function isSaleCategorySelected() {
        // Check the "to" select box (selected categories) in filter_horizontal widget
        // This is where selected categories appear
        var saleSelected = false;
        
        // Check all options in the "to" box (selected categories)
        $('#id_categories_to option').each(function() {
            var optionText = $(this).text().toLowerCase().trim();
            var optionValue = $(this).val();
            
            // Check if it's Sale category by name or value
            if (optionText.includes('sale') || 
                optionText.includes('разпродажба') ||
                optionText === 'sale' ||
                optionText === 'разпродажба') {
                saleSelected = true;
                return false; // break
            }
        });
        
        return saleSelected;
    }
    
    // Function to toggle sale_expires_at field visibility
    function toggleSaleExpiresField() {
        // Find the Sale Settings fieldset
        var saleExpiresFieldset = $('fieldset:has(.field-sale_expires_at)');
        
        if (saleExpiresFieldset.length === 0) {
            // Try alternative selector
            saleExpiresFieldset = $('.field-sale_expires_at').closest('fieldset');
        }
        
        if (saleExpiresFieldset.length > 0) {
            if (isSaleCategorySelected()) {
                saleExpiresFieldset.show();
                // Also expand if collapsed
                saleExpiresFieldset.removeClass('collapsed');
            } else {
                saleExpiresFieldset.hide();
            }
        }
    }
    
    // Run on page load
    $(document).ready(function() {
        // Wait a bit for the page to fully load
        setTimeout(function() {
            toggleSaleExpiresField();
            
            // Watch for changes in categories selection
            $('#id_categories_from, #id_categories_to').on('change', function() {
                setTimeout(toggleSaleExpiresField, 50);
            });
            
            // Watch for clicks on the add/remove buttons in filter_horizontal
            $(document).on('click', '#id_categories_add_link, #id_categories_remove_link', function() {
                setTimeout(toggleSaleExpiresField, 200);
            });
            
            // Watch for double-click events (used by filter_horizontal)
            $(document).on('dblclick', '#id_categories_from option, #id_categories_to option', function() {
                setTimeout(toggleSaleExpiresField, 100);
            });
        }, 100);
    });
    
    // Also check periodically in case of dynamic updates
    var checkInterval = setInterval(function() {
        toggleSaleExpiresField();
    }, 1000);
    
    // Clear interval after 30 seconds to avoid performance issues
    setTimeout(function() {
        clearInterval(checkInterval);
    }, 30000);
    
})(django.jQuery);

