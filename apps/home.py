import dash_html_components as html
import dash_bootstrap_components as dbc

# needed only if running this as a single page app
#external_stylesheets = [dbc.themes.LUX]

#app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# change to app.layout if running as single page app instead
layout = html.Div([
    dbc.Container([
        dbc.Row([
            dbc.Col(html.H1("Welcome to the GNI and VAT revenue checks dashboard", className="text-center")
                    , className="mb-5 mt-5")
        ]),
        dbc.Row([
            dbc.Col(html.H5(children='Web application and dashboard for the analysis of VAT/GNI revenue payments for 2020 '
                                     )
                    , className="mb-4")
            ]),

        dbc.Row([
            dbc.Col(html.H5(children='It consists of three main pages: (1) Upload files, which uploads the files containing the required data, '
                                     '(2) Run tests, which will first pre-process the data files and then run the audit tests, and '
                                     '(3) Analytics dasboard, which provides a visual overview of the data and the test results')
                    , className="mb-5")
        ]),

        dbc.Row([
            dbc.Col(dbc.Card(children=[html.H3(children='Upload the data files required for analysis',
                                               className="text-center"),
                                       dbc.Button("Upload data",
                                                  href="/file_upload",
                                                  color="primary",
                                                  className="mt-3"),
                                       ],
                             body=True, color="dark", outline=True)
                    , width=4, className="mb-4"),

            dbc.Col(dbc.Card(children=[html.H3(children='Run the audit checks for GNI and VAT',
                                               className="text-center"),
                                       dbc.Button("Run checks",
                                                  href="/preprocess_checks",
                                                  color="primary",
                                                  className="mt-3"),
                                       ],
                             body=True, color="dark", outline=True)
                    , width=4, className="mb-4"),

            dbc.Col(dbc.Card(children=[html.H3(children='Look at the dashboard for visual analytics',
                                               className="text-center"),
                                       dbc.Button("See the dashboard",
                                                  href="/GNI_dash",
                                                  color="primary",
                                                  className="mt-3"),

                                       ],
                             body=True, color="dark", outline=True)
                    , width=4, className="mb-4")
        ], className="mb-5"),

        html.A("An automation pilot project by Chamber V and the ECALab.",
               href="https://www.eca.europa.eu")

    ])

])

# needed only if running this as a single page app
# if __name__ == '__main__':
#     app.run_server(host='127.0.0.1', debug=True)