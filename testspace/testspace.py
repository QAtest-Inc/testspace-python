import os
import requests
import subprocess


class Testspace:
    def __init__(self, token, url, project=None, space=None, verify=True):
        self.project = project
        self.space = space
        self.verify = verify

        self.token = token
        if ":" not in token:
            self.token = "{}:".format(token)

        split_url = url.split("://")
        if len(split_url) > 1 and split_url[0] in ["http", "https"]:
            self.url = url
        else:
            self.url = "{}://{}".format("https", url)

    def push(
        self,
        file=None,
        how=None,
        result_name=None,
        build_url=None,
        repo=None,
        link=None,
        message=None,
        project=None,
        space=None,
    ):
        if project is None:
            project = self.project

        if space is None:
            space = self.space

        if project is None or space is None:
            raise ValueError

        command_args_list = ["testspace"]

        if file is not None:
            command_args_list.append(file)

        full_client_url = "/".join([self.url, project, space])

        if how is not None:
            if how not in ["full", "start", "add", "finish"]:
                raise ValueError
            full_client_url = "{}?{}".format(full_client_url, how)
        if result_name is not None:
            full_client_url = "{}#{}".format(full_client_url, result_name)
        command_args_list.append(full_client_url)

        if build_url is not None:
            command_args_list.append("--build-url={}".format(build_url))
        if repo is not None:
            command_args_list.append("--repo={}".format(repo))
        if link is not None:
            command_args_list.append("--link={}".format(link))
        if message is not None:
            command_args_list.append("--message={}".format(message))

        subprocess.run(
            command_args_list,
            check=True,
            env=dict(os.environ, TESTSPACE_TOKEN=self.token),
        )

    def get_api_endpoints(self):
        return self.get_request_json()

    def get_projects(self, limit=30):
        return self.get_request_json(path=self.get_projects_path(), limit=limit)

    def get_project(self, project=None):
        return self.get_request_json(path=self.get_project_path(project))

    def get_spaces(self, project=None, limit=30):
        return self.get_request_json(path=self.get_spaces_path(project), limit=limit)

    def get_space(self, project=None, space=None):
        return self.get_request_json(path=self.get_space_path(project, space))

    def get_results(self, project=None, space=None, limit=30):
        return self.get_request_json(
            path=self.get_results_path(project, space), limit=limit
        )

    def get_result(self, result, project=None, space=None):
        return self.get_request_json(path=self.get_result_path(result, project, space))

    def get_result_failures(self, result, project=None, space=None, limit=30):
        return self.get_request_json(
            path="/".join([self.get_result_path(result, project, space), "failures"]),
            limit=limit,
        )

    def get_result_contents(
        self, result, contents_path=None, project=None, space=None, limit=30
    ):
        if contents_path is None:
            contents_path = "contents"
        elif contents_path.startswith("contents") is not True:
            contents_path = "/".join(["contents", contents_path])
        return self.get_request_json(
            path="/".join(
                [self.get_result_path(result, project, space), contents_path]
            ),
            limit=limit,
        )

    def get_metrics(self, project=None, space=None, limit=30):
        return self.get_request_json(self.get_metrics_path(project, space), limit=limit)

    def get_metric(self, metric, project=None, space=None):
        return self.get_request_json(self.get_metric_path(metric, project, space))

    def get_metric_datasets(self, metric, project=None, space=None, limit=30):
        return self.get_request_json(
            "/".join([self.get_metric_path(metric, project, space), "datasets"]),
            limit=limit,
        )

    def post_projects(self, payload):
        return self.post_request_json(path=self.get_projects_path(), payload=payload)

    def post_spaces(self, payload, project=None):
        return self.post_request_json(
            path=self.get_spaces_path(project=project), payload=payload
        )

    def post_results(self, payload, project=None, space=None):
        return self.post_request_json(
            path=self.get_results_path(project=project, space=space), payload=payload
        )

    def post_metrics(self, payload, project=None, space=None):
        return self.post_request_json(
            path=self.get_metrics_path(project=project, space=space), payload=payload
        )

    def patch_project(self, payload, project=None):
        return self.patch_request(
            path=self.get_project_path(project=project), payload=payload
        )

    def patch_space(self, payload, project=None, space=None):
        return self.patch_request(
            path=self.get_space_path(project=project, space=space), payload=payload
        )

    def patch_metric(self, payload, metric, project=None, space=None):
        return self.patch_request(
            path=self.get_metric_path(metric, project=project, space=space),
            payload=payload,
        )

    def patch_result(self, payload, result):
        return self.patch_request(path=self.get_result_path(result), payload=payload)

    def delete_project(self, project=None):
        return self.delete_request(path=self.get_project_path(project=project))

    def delete_space(self, project=None, space=None):
        return self.delete_request(
            path=self.get_space_path(project=project, space=space)
        )

    def delete_result(self, result, project=None, space=None):
        return self.delete_request(
            path=self.get_result_path(result, project=project, space=space)
        )

    def delete_metric(self, metric, project=None, space=None):
        return self.delete_request(
            path=self.get_metric_path(metric, project=project, space=space)
        )

    def get_request(self, path=None):
        response = self._api_request("GET", path=path)
        return response

    def get_request_json(self, path=None, limit=30):
        if limit is None:
            pass
        elif type(limit) is not int or limit <= 0:
            raise ValueError
        response = self.get_request(path)
        response_json = response.json()
        if type(response_json) is list:
            next_url = response.links.get("next", None)
            while next_url is not None:
                if limit is not None and len(response_json) >= limit:
                    break
                response = self.get_request(next_url.get("url"))
                next_url = response.links.get("next", None)
                response_json.extend(response.json())
            response_json = response_json[:limit]
        return response_json

    def post_request(self, payload, path=None):
        response = self._api_request("POST", path=path, payload=payload)
        return response

    def post_request_json(self, payload, path=None):
        response = self.post_request(payload, path=path)
        return response.json()

    def patch_request(self, payload, path=None):
        response = self._api_request("PATCH", path=path, payload=payload)
        return response

    def delete_request(self, path=None):
        response = self._api_request("DELETE", path=path)
        return response

    def get_api_url(self):
        return "/".join([self.url, "api"])

    def get_projects_path(self):
        return "projects"

    def get_project_path(self, project=None):
        if project is None:
            if self.project is not None:
                project = self.project
            else:
                raise ValueError
        return "/".join([self.get_projects_path(), self._url_escape(project)])

    def get_spaces_path(self, project=None):
        return "/".join([self.get_project_path(project), "spaces"])

    def get_space_path(self, project=None, space=None):
        if project is None and type(space) is int:
            return "/".join(["spaces", str(space)])
        elif space is None:
            if self.space is not None:
                space = self.space
            else:
                raise ValueError
        return "/".join([self.get_spaces_path(project), self._url_escape(space)])

    def get_results_path(self, project=None, space=None):
        return "/".join([self.get_space_path(project, space), "results"])

    def get_result_path(self, result, project=None, space=None):
        return "/".join([self.get_results_path(project, space), self._url_escape(result)])

    def get_metrics_path(self, project=None, space=None):
        return "/".join([self.get_space_path(project, space), "metrics"])

    def get_metric_path(self, metric, project=None, space=None):
        metric_str = str(metric)
        if str.isdigit(metric_str) is not True:
            raise ValueError
        return "/".join([self.get_metrics_path(project, space), metric_str])

    def _api_request(self, method, path, payload=None):
        if path is None:
            request_url = self.get_api_url()
        elif self.get_api_url() in path:
            request_url = path
        else:
            request_url = "/".join([self.get_api_url(), path])
        response = requests.request(
            method=method,
            url=request_url,
            verify=self.verify,
            auth=tuple(self.token.split(":", 1)),
            json=payload,
        )
        response.raise_for_status()
        return response

    def _url_escape(self, value):
        return requests.utils.quote(str(value), safe='')
