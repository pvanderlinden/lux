    function addPageInfo(page, $scope, dateFilter, $lux) {
        if (page.head && page.head.title) {
            document.title = page.head.title;
        }
        if (page.author) {
            if (page.author instanceof Array)
                page.authors = page.author.join(', ');
            else
                page.authors = page.author;
        }
        var date;
        if (page.date) {
            try {
                date = new Date(page.date);
            } catch (e) {
                $lux.log.error('Could not parse date');
            }
            page.date = date;
            page.dateText = dateFilter(date, $scope.dateFormat);
        }
        page.toString = function () {
            return this.name || this.url || '<noname>';
        };

        return page;
    }

    //  Lux angular
    //  ==============
    //  Lux main module for angular. Design to work with the ``lux.extension.angular``
    angular.module('lux.page', ['lux.services', 'lux.form', 'lux.scroll', 'templates-page'])
        //
        .controller('Page', ['$scope', '$log', '$lux', 'dateFilter', function ($scope, log, $lux, dateFilter) {
            //
            $lux.log.info('Setting up angular page');
            //
            var page = $scope.page;
            // If the page is a string, retrieve it from the pages object
            if (typeof page === 'string')
                page = $scope.pages ? $scope.pages[page] : null;
            $scope.page = addPageInfo(page || {}, $scope, dateFilter, $lux);
            //
            // logout via post method
            $scope.logout = function(e, url) {
                e.preventDefault();
                e.stopPropagation();
                $lux.post(url).success(function (data) {
                    if (data.redirect)
                        window.location.replace(data.redirect);
                });
            };

            $scope.togglePage = function ($event) {
                $event.preventDefault();
                $event.stopPropagation();
                this.link.active = !this.link.active;
            };

            $scope.loadPage = function ($event) {
                $scope.page = this.link;
            };

            $scope.activeLink = function (url) {
                var loc;
                if (isAbsolute.test(url))
                    loc = $lux.location.absUrl();
                else
                    loc = window.location.pathname;
                var rest = loc.substring(url.length),
                    base = loc.substring(0, url.length),
                    folder = url.substring(url.length-1) === '/';
                return base === url && (folder || (rest === '' || rest.substring(0, 1) === '/'));
            };

            //
            $scope.$on('animIn', function() {
                log.info('Page ' + page.toString() + ' animation in');
            });
            $scope.$on('animOut', function() {
                log.info('Page ' + page.toString() + ' animation out');
            });
        }])
        .service('$breadcrumbs', [function () {

            this.crumbs = function () {
                var loc = window.location,
                    path = loc.pathname,
                    steps = [],
                    last = {
                        href: loc.origin
                    };
                if (last.href.length >= lux.context.url.length)
                    steps.push(last);

                path.split('/').forEach(function (name) {
                    if (name) {
                        last = {
                            label: name,
                            href: joinUrl(last.href, name+'/')
                        };
                        if (last.href.length >= lux.context.url.length)
                            steps.push(last);
                    }
                });
                if (steps.length) {
                    last = steps[steps.length-1];
                    if (path.substring(path.length-1) !== '/' && last.href.substring(last.href.length-1) === '/')
                        last.href = last.href.substring(0, last.href.length-1);
                    last.last = true;
                    steps[0].label = 'Home';
                }
                return steps;
            };
        }])
        //
        //  Directive for displaying breadcrumbs navigation
        .directive('breadcrumbs', ['$breadcrumbs', '$rootScope', function ($breadcrumbs, $rootScope) {
            return {
                restrict: 'AE',
                replace: true,
                templateUrl: "page/breadcrumbs.tpl.html",
                link: {
                    post: function (scope) {
                        var renderBreadcrumb = function() {
                            scope.steps = $breadcrumbs.crumbs();
                        };

                        $rootScope.$on('$viewContentLoaded', function () {
                            renderBreadcrumb();
                        });

                        renderBreadcrumb();
                    }
                }
            };
        }])
        //
        // Directive for displaying page messages
        //
        //  <div data-options='sitemessages' data-page-messages></div>
        //  <script>
        //      sitemessages = {
        //          messages: [...],
        //          dismissUrl: (Optional url to use when dismissing a message)
        //      };
        //  </script>
        .directive('pageMessages', ['$lux', '$sce', function ($lux, $sce) {

            return {
                restrict: 'AE',
                templateUrl: "page/messages.tpl.html",
                scope: {},
                link: function (scope, element, attrs) {
                    scope.messageClass = {
                        info: 'alert-info',
                        success: 'alert-success',
                        warning: 'alert-warning',
                        danger: 'alert-danger',
                        error: 'alert-danger'
                    };
                    scope.dismiss = function (e, m) {
                        var target = e.target;
                        while (target && target.tagName !== 'DIV')
                            target = target.parentNode;
                        $(target).remove();
                        $lux.post('/_dismiss_message', {message: m});
                    };
                    var messages = getOptions(attrs);
                    scope.messages = [];
                    forEach(messages, function (message) {
                        if (message) {
                            if (typeof(message) === 'string')
                                message = {body: message};
                            message.body = $sce.trustAsHtml(message.body);
                        }
                        scope.messages.push(message);
                    });
                }
            };
        }]);