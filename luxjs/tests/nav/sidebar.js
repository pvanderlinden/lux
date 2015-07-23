
    describe("Test sidebar", function() {

        var digest = function($compile, $rootScope, template) {
                var scope = $rootScope.$new(),
                    element = $compile(template)(scope);
                scope.$digest();
                return element;
            };

        beforeEach(function () {
            module('lux.sidebar');
        });

        it("sidebar + navbar with user check: directive defaults", inject(function($compile, $rootScope) {
            var sidebar = digest($compile, $rootScope, '<sidebar></sidebar>');
            var div = angular.element(sidebar.children()[0]);
            var navbar = angular.element(div.children()[0]);
            var aside = angular.element(div.children()[1]);
            var nav = angular.element(navbar.children()[0]);
            var container = angular.element(nav.children()[0]);
            var navbarHeader = angular.element(container.children()[0]);

            expect(sidebar[0].tagName).toBe('SIDEBAR');
            expect(div[0].tagName).toBe('DIV');
            expect(aside[0].tagName).toBe('ASIDE');
            expect(aside.hasClass('main-sidebar')).toBe(true);
            expect(aside.attr('id')).toBeUndefined();
            expect(navbar[0].tagName).toBe('NAVBAR');
            expect(nav[0].tagName).toBe('NAV');

            expect(nav.hasClass('navbar')).toBe(true);

            expect(sidebar.children().length).toBe(2);

            // Instead of this if statement, there should be 2 separate tests.
            if ($rootScope.user) {
                expect(navbarHeader.children().length).toBe(3);
            } else {
                expect(navbarHeader.children().length).toBe(2);
            }
        }));
/*
        it("sidebar + navbar directive with data", inject(function($compile, $rootScope) {
            var template = '<sidebar data-position="left" data-id="sidebar1"></navbar>',
                element = digest($compile, $rootScope, template),
                body = angular.element('body');
            //
            if ($rootScope.user) {
                var sidebar = angular.element(element.children()[1]);

                expect(element.children().length).toBe(2);
                expect(sidebar[0].tagName).toBe('ASIDE');
                expect(sidebar.attr('id')).toBe('sidebar1');
                expect(body.hasClass('left-sidebar')).toBe(true);
            } else {
                expect(element.children().length).toBe(1);
            }
         }));

        it("sidebar + navbar directive with options from object", inject(function($compile, $rootScope) {
            lux.context._sidebar = {
                id: 'sidebar1',
                position: 'right',
                collapse: true,
                toggle: false,
                sections: [{
                    name: 'Section1',
                    items: [{
                        name: 'Item1',
                        icon: 'fa fa-dashboard',
                        subitems: [
                            {
                                href: '#',
                                name: 'Dashbaord',
                                icon: 'fa fa-dashboard'
                            }
                        ]
                    }]
                }]
            };
            var template = '<sidebar data-options="lux.context._sidebar"></sidebar>',
                element = digest($compile, $rootScope, template),
                body = angular.element('body');
            delete lux.context._sidebar;
            //
            if ($rootScope.user) {
                var sidebar = angular.element(element.children()[1]);

                expect(element.children().length).toBe(2);
                expect(sidebar[0].tagName).toBe('ASIDE');
                expect(sidebar.hasClass('main-sidebar')).toBe(true);
                expect(sidebar.attr('id')).toBe('sidebar1');
                expect(body.hasClass('right-sidebar')).toBe(true);
            } else {
                expect(element.children().length).toBe(1);
            }
        }));
*/
    });
